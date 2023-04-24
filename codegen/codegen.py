### Generation script for boilerplate euint type system

f = open("Common.sol", "w")
f.write("""\
// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

type euint8 is uint256;
type euint16 is uint256;
type euint32 is uint256;

library Common {
// Values used to communicate types at runtime to the cast() precompile.
    uint8 internal constant euint8_t = 0;
    uint8 internal constant euint16_t = 1;
    uint8 internal constant euint32_t = 2;
}
"""
)
f.close()

f = open("Precompiles.sol", "w")
f.write("""\
// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

library Precompiles {
    uint256 public constant Add = 65;
    uint256 public constant Verify = 66;
    uint256 public constant Reencrypt = 67;
    uint256 public constant Delegate = 68;
    uint256 public constant Require = 69;
    uint256 public constant LessThanOrEqual = 70;
    uint256 public constant Subtract = 71;
    uint256 public constant Multiply = 72;
    uint256 public constant LessThan = 73;
    uint256 public constant Random = 74;
    uint256 public constant OptimisticRequire = 75;
    uint256 public constant Cast = 76;
}
"""
)
f.close()

f = open("Impl.sol", "w")
f.write("""\
// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import "./Precompiles.sol";

library Impl {
    uint256 constant euint8Size = 32 + 28124;
    uint256 constant euint16Size = 32 + 56236;
    uint256 constant euint32Size = 32 + 112460;

    function add(uint256 a, uint256 b) internal view returns (uint256 result) {
        if (a == 0) {
            return b;
        } else if (b == 0) {
            return a;
        }
        bytes32[2] memory input;
        input[0] = bytes32(a);
        input[1] = bytes32(b);
        uint256 inputLen = 64;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the add precompile.
        uint256 precompile = Precompiles.Add;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, output, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(output[0]);
    }

    function sub(uint256 a, uint256 b) internal view returns (uint256 result) {
        if (a == 0) {
            return b;
        } else if (b == 0) {
            return a;
        }
        bytes32[2] memory input;
        input[0] = bytes32(a);
        input[1] = bytes32(b);
        uint256 inputLen = 64;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the sub precompile.
        uint256 precompile = Precompiles.Subtract;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, output, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(output[0]);
    }

    function mul(uint256 a, uint256 b) internal view returns (uint256 result) {
        if (a == 0) {
            return b;
        } else if (b == 0) {
            return a;
        }
        bytes32[2] memory input;
        input[0] = bytes32(a);
        input[1] = bytes32(b);
        uint256 inputLen = 64;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the mul precompile.
        uint256 precompile = Precompiles.Multiply;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, output, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(output[0]);
    }

    // Evaluate `lhs <= rhs` on the given ciphertexts and, if successful, return the resulting ciphertext.
    // If successful, the resulting ciphertext is automatically verified.
    function lte(uint256 lhs, uint256 rhs) internal view returns (uint256 result) {
        bytes32[2] memory input;
        input[0] = bytes32(lhs);
        input[1] = bytes32(rhs);
        uint256 inputLen = 64;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the lte precompile.
        uint256 precompile = Precompiles.LessThanOrEqual;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, output, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(output[0]);
    }

    // Evaluate `lhs < rhs` on the given ciphertexts and, if successful, return the resulting ciphertext.
    // If successful, the resulting ciphertext is automatically verified.
    function lt(uint256 lhs, uint256 rhs) internal view returns (uint256 result) {
        bytes32[2] memory input;
        input[0] = bytes32(lhs);
        input[1] = bytes32(rhs);
        uint256 inputLen = 64;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the lte precompile.
        uint256 precompile = Precompiles.LessThan;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, output, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(output[0]);
    }
    
    // If `control`'s value is 1, the resulting value is the same value as `ifTrue`.
    // If `control`'s value is 0, the resulting value is the same value as `ifFalse`.
    // If successful, the resulting ciphertext is automatically verified.
    function cmux(uint256 control, uint256 ifTrue, uint256 ifFalse) internal view returns (uint256 result) {
        // result = (ifTrue - ifFalse) * control + ifFalse

        bytes32[2] memory input;
        uint256 inputLen = 64;
        uint256 outputLen = 32;

        // Call the sub precompile.
        input[0] = bytes32(ifTrue);
        input[1] = bytes32(ifFalse);
        uint256 precompile = Precompiles.Subtract;
        bytes32[1] memory subOutput;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, subOutput, outputLen)) {
                revert(0, 0)
            }
        }

        // Call the mul precompile.
        input[0] = bytes32(control);
        input[1] = bytes32(subOutput[0]);
        precompile = Precompiles.Multiply;
        bytes32[1] memory mulOutput;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, mulOutput, outputLen)) {
                revert(0, 0)
            }
        }

        // Call the add precompile.
        input[0] = bytes32(mulOutput[0]);
        input[1] = bytes32(ifFalse);
        precompile = Precompiles.Add;
        bytes32[1] memory addOutput;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, addOutput, outputLen)) {
                revert(0, 0)
            }
        }

        result = uint256(addOutput[0]);
    }
    
    // Optimistically requires that the `ciphertext` is true.
    //
    // This function does not evaluate the given `ciphertext` at the time of the call.
    // Instead, it accumulates all optimistic requires and evaluates a single combined
    // require at the end through the decryption oracle. A side effect of this mechanism
    // is that a method call with a failed optimistic require will always incur the full
    // gas cost, as if all optimistic requires were true. Yet, the transaction will be
    // reverted at the end if any of the optimisic requires were false.
    //
    // The benefit of optimistic requires is that they are faster than non-optimistic ones,
    // because there is a single call to the decryption oracle per transaction, irrespective
    // of how many optimistic requires were used.
    function optimisticRequireCt(uint256 ciphertext) internal view {
        bytes32[1] memory input;
        input[0] = bytes32(ciphertext);
        uint256 inputLen = 32;

        // Call the optimistic require precompile.
        uint256 precompile = Precompiles.OptimisticRequire;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, 0, 0)) {
                revert(0, 0)
            }
        }
    }

//    function safeAdd(uint256 a, uint256 b) internal view returns (uint256) {
//        TODO: Call addSafe() precompile.
//        return 0;
//    }

    function cast(uint256 ciphertext, uint8 toType) internal view returns(uint256) {
        bytes memory input = bytes.concat(bytes32(ciphertext), bytes1(toType));
        uint256 inputLen = input.length;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the cast precompile.
        uint256 precompile = Precompiles.Cast;
        assembly {
            if iszero(
                staticcall(
                    gas(),
                    precompile,
                    add(input, 32), // jump over the 32-bit `size` field of the `bytes` data structure to read actual bytes
                    inputLen,
                    output,
                    outputLen
                )
            ) {
                revert(0, 0)
            }
        }
        return 0;
    }

    function reencrypt(uint256 ciphertext, uint8 _type) internal view returns (bytes memory reencrypted) {
        bytes32[1] memory input;
        input[0] = bytes32(ciphertext);
        uint256 inputLen = 32;

        uint256 MaxCiphertextBytesLen;

        if (_type == 0) {
            MaxCiphertextBytesLen = euint8Size;
        } else if (_type == 1) {
            MaxCiphertextBytesLen = euint16Size;
        } else if (_type == 2) {
            MaxCiphertextBytesLen = euint32Size;
        } else {
            revert("unsupported ciphertext type");
        }
        
        // Call the reencrypt precompile.
        uint256 precompile = Precompiles.Reencrypt;
        assembly {
            if iszero(
                staticcall(
                    gas(),
                    precompile,
                    input,
                    inputLen,
                    reencrypted,
                    MaxCiphertextBytesLen
                )
            ) { 
                revert(0, 0)
            }
        }
    }

    function verify(
        bytes memory _ciphertextBytes,
        uint8 _toType
    ) internal view returns (uint256 result) {
        bytes memory input = bytes.concat(_ciphertextBytes, bytes1(_toType));
        uint256 inputLen = input.length;

        bytes32[1] memory output;
        uint256 outputLen = 32;

        // Call the cast precompile.
        uint256 precompile = Precompiles.Verify;
        assembly {
            if iszero(
                staticcall(
                    gas(),
                    precompile,
                    add(input, 32), // jump over the 32-bit `size` field of the `bytes` data structure to read actual bytes
                    inputLen,
                    output,
                    outputLen
                )
            ) {
                revert(0, 0)
            }
        }
        result = uint256(output[0]);
        return 0;
    }

    function delegate(uint256 ciphertext) internal view {
        bytes32[1] memory input;
        input[0] = bytes32(ciphertext);
        uint256 inputLen = 32;

        // Call the delegate precompile
        uint256 precompile = Precompiles.Delegate;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, 0, 0)) {
                revert(0, 0)
            }
        }
    }

    function requireCt(uint256 ciphertext) internal view {
        bytes32[1] memory input;
        input[0] = bytes32(ciphertext);
        uint256 inputLen = 32;

        // Call the require precompile.
        uint256 precompile = Precompiles.Require;
        assembly {
            if iszero(staticcall(gas(), precompile, input, inputLen, 0, 0)) {
                revert(0, 0)
            }
        }
    }
}
"""
)
f.close()

f = open("FHEOps.sol", "w")
f.write("""\
// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import "./Common.sol";
import "./Impl.sol";
library FHEOps {""")

to_print =  """
    function {f}(euint{i} a, euint{j} b) internal view returns (euint{k}) {{
        return euint{k}.wrap(Impl.{f}(euint{i}.unwrap(a), euint{j}.unwrap(b)));
    }}
"""

for i in (2**p for p in range(3, 6)):
    for j in (2**p for p in range(3, 6)):
        if i == j: # TODO: remove this line when casting is implemented
            f.write(to_print.format(i=i, j=j, k=i if i>j else j, f="add"))
            f.write(to_print.format(i=i, j=j, k=i if i>j else j, f="sub"))
            f.write(to_print.format(i=i, j=j, k=i if i>j else j, f="mul"))
            f.write(to_print.format(i=i, j=j, k=8, f="lte"))
            f.write(to_print.format(i=i, j=j, k=8, f="lt"))

to_print =  """
    function cmux(euint8 control, euint{i} a, euint{j} b) internal view returns (euint{k}) {{
        return euint{k}.wrap(Impl.cmux(euint8.unwrap(control), euint{i}.unwrap(a), euint{j}.unwrap(b)));
    }}
"""
for i in (2**p for p in range(3, 6)):
    for j in (2**p for p in range(3, 6)):
        if i == j: # TODO: remove this line when casting is implemented
            f.write(to_print.format(i=i, j=j, k=i if i>j else j))


to_print="""
    function toEuint{i}(euint{j} v) internal view returns (euint{i}) {{
        return euint{i}.wrap(Impl.cast(euint{j}.unwrap(v), Common.euint{j}_t));
    }}
"""

for i in (2**p for p in range(3, 6)):
    for j in (2**q for q in range(3, 6)):
        if (i != j):
            f.write(to_print.format(i=i, j=j))

f.write("}")
f.close

f = open("Ciphertext.sol", "w")
f.write("""\
// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import "./Common.sol";
import "./Impl.sol";

library Ciphertext {""")

to_print="""
    function asEuint{i}(bytes memory ciphertext) internal view returns (euint{i}) {{
        return euint{i}.wrap(Impl.verify(ciphertext, Common.euint{i}_t));
    }}

    function reencrypt(euint{i} ciphertext) internal view returns (bytes memory reencrypted) {{
        return Impl.reencrypt(euint{i}.unwrap(ciphertext), Common.euint{i}_t);
    }}

    function delegate(euint{i} ciphertext) internal view {{
        Impl.delegate(euint{i}.unwrap(ciphertext));
    }}
"""

for i in (2**p for p in range(3, 6)):
    f.write(to_print.format(i=i))

f.write("""
    function requireCt(euint8 ciphertext) internal view {{
        Impl.requireCt(euint8.unwrap(ciphertext));
    }}
    function optimisticRequireCt(euint8 ciphertext) internal view {{
        Impl.optimisticRequireCt(euint8.unwrap(ciphertext));
    }}
""")

f.write("}")
f.close()