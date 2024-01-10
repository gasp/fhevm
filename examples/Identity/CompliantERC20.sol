// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity ^0.8.20;

import "../../lib/TFHE.sol";
import "../../abstracts/Reencrypt.sol";
import "../EncryptedERC20.sol";
import "./ERC20Rules.sol";
import "./IdentityRegistry.sol";

contract CompliantERC20 is EncryptedERC20 {
    IdentityRegistry identityContract;
    ERC20Rules rulesContract;

    constructor(address _identityAddr, address _rulesAddr) {
        identityContract = IdentityRegistry(_identityAddr);
        rulesContract = ERC20Rules(_rulesAddr);
    }

    function identifiers() public view returns (string[] memory) {
        return rulesContract.getIdentifiers();
    }

    function getIdentifier(address wallet, string calldata identifier) external view returns (euint32) {
        require(msg.sender == address(rulesContract), "Access restricted to the current ERC20Rules");
        return identityContract.getIdentifier(wallet, identifier);
    }

    function balanceOf(
        address wallet,
        bytes32 publicKey,
        bytes calldata signature
    ) public view override onlySignedPublicKey(publicKey, signature) returns (bytes memory) {
        if (wallet == msg.sender) {
            return TFHE.reencrypt(balances[msg.sender], publicKey, 0);
        }

        uint32 userCountry = rulesContract.whitelistedWallets(msg.sender);
        require(userCountry > 0, "You're not registered as a country wallet");

        euint32 walletCountry = identityContract.getIdentifier(wallet, "country");
        ebool sameCountry = TFHE.eq(walletCountry, userCountry);
        euint32 balance = TFHE.isInitialized(balances[wallet]) ? balances[wallet] : TFHE.asEuint32(0);
        balance = TFHE.cmux(sameCountry, balance, TFHE.asEuint32(0));

        return TFHE.reencrypt(balance, publicKey, 0);
    }

    // Transfers an encrypted amount.
    function _transfer(address from, address to, euint32 _amount, ebool isTransferable) internal override {
        // Condition 1: hasEnoughFunds
        ebool enoughFund = TFHE.le(_amount, balances[from]);
        euint32 amount = TFHE.cmux(enoughFund, _amount, TFHE.asEuint32(0));

        amount = rulesContract.transfer(from, to, amount);

        balances[to] = balances[to] + amount;
        balances[from] = balances[from] - amount;
    }
}