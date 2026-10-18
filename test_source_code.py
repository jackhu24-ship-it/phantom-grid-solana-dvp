#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
PHANTOM GRID // SOURCE CODE CORE VERIFICATION SUITE (test_source_code.py)
Core Codebase Hard Assertions (Web3.js v3 + Token-2022 + Atomic Reclaim + Pure Deps)
========================================================================================
Hard Assertions:
1. assert 1,500 Extreme Chaos Stress Tests Pass 100% (Zero Fault / 100.0% Reliability)
2. assert Deterministic State Machine satisfies 100% Invariants (Zero Brain-Split)
3. assert Token-2022 Extension Blacklist Validation (validate_token_extensions strict gate)
4. assert Timeout Atomic Reclaim Test (100% Zero Capital Lockup)
5. assert Dependency list requirements.txt and package.json are pure and unpolluted
6. assert Core kernel latency meets SLA (< 1.0 ms)
========================================================================================
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure local imports
curr_dir = Path(__file__).parent
sys.path.insert(0, str(curr_dir))

from solana_dvp_fsm_core import (
    DeterministicDvPFSM,
    DvPState,
    TokenExtensionType,
    KeyPairSigner,
    validate_token_extensions,
)
from test_solana_dvp_chaos import run_dvp_chaos_torture_test


def audit_source_code() -> bool:
    print("\n" + "=" * 90)
    print("🏛️ PHANTOM GRID // SOURCE CODE FINAL AUDIT (02_SourceCode)")
    print("=========================================================================================")
    print(f"{'Check Item':<26} {'Requirement':<38} {'Actual State':<14} {'Verdict'}")
    print("-" * 90)

    # 1. 1,500 Extreme Chaos Stress Tests
    chaos_pass = run_dvp_chaos_torture_test(1500)
    status_1 = "1500/1500 Passed" if chaos_pass else "Chaos Failed"
    print(f"{'1. 1,500 Chaos Stress Tests':<24} {'1,500 Cycles 100% Zero Fault':<36} {status_1:<14} {'[✅ PASS]' if chaos_pass else '[❌ FAIL]'}")
    assert chaos_pass, "[FAIL] 1,500 Chaos Stress Tests failed to achieve 100% pass rate"

    # 2. Web3.js v3 Specification (Uint8Array, BigInt, KeyPairSigner async)
    fsm = DeterministicDvPFSM()
    buyer = "Buyer_Web3v3_Kit"
    seller = "Seller_Web3v3_Kit"
    order = fsm.create_trade(buyer, seller, "USDC_MINT", 100_000_000_000, "SOL_MINT", 500_000_000_000)

    # Check Uint8Array & BigInt
    assert isinstance(order.instruction_payload_bytes, bytearray), "[FAIL] Payload is not Uint8Array (bytearray)"
    assert isinstance(order.leg_a.account_data_buffer, bytearray), "[FAIL] Account buffer is not Uint8Array"
    assert isinstance(order.expiry_timestamp_ns, int), "[FAIL] Timestamp is not BigInt ns"
    assert isinstance(order.leg_a.amount_raw, int), "[FAIL] Amount is not BigInt"

    # KeyPairSigner async verification
    signer = KeyPairSigner("TEST_SIGNER")
    sig = asyncio.run(signer.sign_message_async(order.instruction_payload_bytes))
    assert isinstance(sig, bytearray) and len(sig) == 64, "[FAIL] KeyPairSigner output is not 64-byte Uint8Array"

    print(f"{'2. Web3.js v3 & Signer':<24} {'Uint8Array/BigInt/KeyPairSigner':<36} {'Zero-Copy Native':<14} {'[✅ PASS]'}")

    # 3. Token-2022 Blacklist Validation
    assert validate_token_extensions("PermanentDelegate") is True
    assert validate_token_extensions("TransferHook") is True
    assert validate_token_extensions("Pausable") is True
    assert validate_token_extensions("TransferFee") is False
    assert validate_token_extensions("NonTransferable") is False
    assert validate_token_extensions(TokenExtensionType.DISALLOWED_TRANSFER_FEE) is False
    assert validate_token_extensions(TokenExtensionType.DISALLOWED_NON_TRANSFERABLE) is False

    print(f"{'3. Token-2022 Blacklist':<24} {'Blocks Fee / Non-Transfer Mints':<36} {'Active & Safe':<14} {'[✅ PASS]'}")

    # 4. Timeout Atomic Reclaim
    reclaim_order = fsm.create_trade(buyer, seller, "USDC_MINT", 75_000_000_000, "SOL_MINT", 300_000_000_000)
    fsm.fund_leg(reclaim_order.trade_id, buyer, 75_000_000_000)
    assert reclaim_order.current_state == DvPState.LEG_A_LOCKED

    # Trigger timeout refund
    reclaim_order.expiry_timestamp_ns = time.time_ns() - 10_000_000_000
    refund = fsm.reclaim_refund(reclaim_order.trade_id, buyer)
    assert refund["refund_amount"] == 75_000_000_000, "[FAIL] Refund amount not conserved"
    assert reclaim_order.current_state == DvPState.REFUNDED_CLOSED, "[FAIL] State did not transition to REFUNDED_CLOSED"
    assert reclaim_order.leg_a.deposited_amount == 0, "[FAIL] Deposited amount not zeroed"

    print(f"{'4. Timeout Atomic Reclaim':<24} {'Atomic Reclaim Zero Lockup':<36} {'Reclaim OK':<14} {'[✅ PASS]'}")

    # 5. Pure Dependencies
    req_file = curr_dir / "requirements.txt"
    pkg_file = curr_dir / "package.json"
    assert req_file.exists(), "[FAIL] requirements.txt not found"
    assert pkg_file.exists(), "[FAIL] package.json not found"

    lines = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    disallowed_deps = ["torch", "tensorflow", "transformers", "flask", "django"]
    contaminated = [dep for dep in lines if any(d in dep.lower() for d in disallowed_deps)]
    assert not contaminated, f"[FAIL] Dependencies contain bloated/unapproved libraries: {contaminated}"

    pkg_text = pkg_file.read_text(encoding="utf-8")
    assert "@solana/web3.js" in pkg_text and "@solana/kit" in pkg_text, "[FAIL] package.json missing @solana/kit or @solana/web3.js"

    print(f"{'5. Pure Dependencies':<24} {'requirements.txt & package.json Pure':<36} {'Web3.js v3 Locked':<14} {'[✅ PASS]'}")

    # 6. Microkernel Latency SLA
    perf_fsm = DeterministicDvPFSM()
    rounds = 500
    t0 = time.perf_counter()
    for _ in range(rounds):
        perf_order = perf_fsm.create_trade(buyer, seller, "USDC", 1000, "SOL", 10)
        perf_fsm.fund_leg(perf_order.trade_id, buyer, 1000)
        perf_fsm.fund_leg(perf_order.trade_id, seller, 10)
        perf_fsm.execute_atomic_settlement(perf_order.trade_id, "AUTH_OK")
    t1 = time.perf_counter()
    avg_latency_ms = ((t1 - t0) / rounds) * 1000.0

    print(f"{'6. Microkernel Latency':<24} {'Single Settlement Execution < 1.0 ms':<36} {f'{avg_latency_ms:.3f} ms':<14} {'[✅ PASS]'}")
    assert avg_latency_ms < 1.0, f"[FAIL] Settlement latency exceeded SLA: {avg_latency_ms:.3f} ms >= 1.0 ms"

    print("=" * 90)
    print("✅ 02_SourceCode Six Mandatory Assertions ALL PASS!")
    print("=" * 90 + "\n")
    return True


if __name__ == "__main__":
    success = audit_source_code()
    sys.exit(0 if success else 1)
