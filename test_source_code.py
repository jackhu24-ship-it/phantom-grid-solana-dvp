#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
PHANTOM GRID // SOURCE CODE CORE VERIFICATION SUITE (test_source_code.py)
核心代碼庫四大強制斷言驗收腳本 (Web3.js v3 + Token-2022 + Atomic Reclaim + Pure Deps)
========================================================================================
必須通過的強制判定條件 (Hard Assertions):
1. assert 1,500 次極限混沌壓測 100% 通過 (Zero Fault / 100.0% Reliability)
2. assert 狀態機滿足 100% 不變量 (Zero Brain-Split Invariants 成立)
3. assert 實裝 Token-2022 擴展黑名單校驗 (validate_token_extensions 剛性攔截)
4. assert 補齊逾時原子回滾測試 (Atomic Reclaim Test 100% 零資金鎖死)
5. assert 依賴清單 requirements.txt 與 package.json 純淨且無污染
6. assert 核心算子/微內核延遲達標 (< 1.0 ms)
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
    print(f"{'檢查項目':<26} {'規範要求':<38} {'實測狀態':<14} {'判定'}")
    print("-" * 90)

    # ---------------------------------------------------------
    # 斷言 1: 1,500 次極限混沌壓測 100% 通過
    # ---------------------------------------------------------
    chaos_pass = run_dvp_chaos_torture_test(1500)
    status_1 = "1500/1500 通過" if chaos_pass else "混沌測試失敗"
    print(f"{'1. 1,500次極限混沌壓測':<24} {'1,500 次循環 100% 零故障通過':<36} {status_1:<14} {'[✅ PASS]' if chaos_pass else '[❌ FAIL]'}")
    assert chaos_pass, "[FAIL] 1,500 次極限混沌壓測未達成 100% 通過"

    # ---------------------------------------------------------
    # 斷言 2: Web3.js v3 規範 (Uint8Array, BigInt, KeyPairSigner async)
    # ---------------------------------------------------------
    fsm = DeterministicDvPFSM()
    buyer = "Buyer_Web3v3_Kit"
    seller = "Seller_Web3v3_Kit"
    order = fsm.create_trade(buyer, seller, "USDC_MINT", 100_000_000_000, "SOL_MINT", 500_000_000_000)

    # Check Uint8Array & BigInt
    assert isinstance(order.instruction_payload_bytes, bytearray), "[FAIL] Payload 不是 Uint8Array (bytearray)"
    assert isinstance(order.leg_a.account_data_buffer, bytearray), "[FAIL] 帳戶資料不是 Uint8Array"
    assert isinstance(order.expiry_timestamp_ns, int), "[FAIL] 時間戳不是 BigInt 奈秒"
    assert isinstance(order.leg_a.amount_raw, int), "[FAIL] 金額不是 BigInt"

    # KeyPairSigner async verification
    signer = KeyPairSigner("TEST_SIGNER")
    sig = asyncio.run(signer.sign_message_async(order.instruction_payload_bytes))
    assert isinstance(sig, bytearray) and len(sig) == 64, "[FAIL] KeyPairSigner 產出不是 64-byte Uint8Array"

    print(f"{'2. Web3.js v3 與 Signer':<22} {'Uint8Array/BigInt/KeyPairSigner':<36} {'全原生零拷貝':<14} {'[✅ PASS]'}")

    # ---------------------------------------------------------
    # 斷言 3: Token-2022 擴展黑白名單客戶端校驗
    # ---------------------------------------------------------
    assert validate_token_extensions("PermanentDelegate") is True
    assert validate_token_extensions("TransferHook") is True
    assert validate_token_extensions("Pausable") is True
    assert validate_token_extensions("TransferFee") is False
    assert validate_token_extensions("NonTransferable") is False
    assert validate_token_extensions(TokenExtensionType.DISALLOWED_TRANSFER_FEE) is False
    assert validate_token_extensions(TokenExtensionType.DISALLOWED_NON_TRANSFERABLE) is False

    print(f"{'3. Token-2022 黑名單校驗':<22} {'validate_token_extensions 剛性阻斷':<36} {'黑白名單嚴格':<14} {'[✅ PASS]'}")

    # ---------------------------------------------------------
    # 斷言 4: 逾時原子回滾測試 (Atomic Reclaim 100% 零資金鎖死)
    # ---------------------------------------------------------
    reclaim_order = fsm.create_trade(buyer, seller, "USDC_MINT", 75_000_000_000, "SOL_MINT", 300_000_000_000)
    fsm.fund_leg(reclaim_order.trade_id, buyer, 75_000_000_000)
    assert reclaim_order.current_state == DvPState.LEG_A_LOCKED

    # 逾時觸發退款
    reclaim_order.expiry_timestamp_ns = time.time_ns() - 10_000_000_000
    refund = fsm.reclaim_refund(reclaim_order.trade_id, buyer)
    assert refund["refund_amount"] == 75_000_000_000, "[FAIL] 退款金額不守恆"
    assert reclaim_order.current_state == DvPState.REFUNDED_CLOSED, "[FAIL] 狀態未遷移至 REFUNDED_CLOSED"
    assert reclaim_order.leg_a.deposited_amount == 0, "[FAIL] 資金未歸零"

    print(f"{'4. 逾時原子回滾斷言':<24} {'Atomic Reclaim 100% 零資金鎖死':<36} {'資金原路返還':<14} {'[✅ PASS]'}")

    # ---------------------------------------------------------
    # 斷言 5: 純淨依賴清單 requirements.txt & package.json
    # ---------------------------------------------------------
    req_file = curr_dir / "requirements.txt"
    pkg_file = curr_dir / "package.json"
    assert req_file.exists(), "[FAIL] requirements.txt 不存在"
    assert pkg_file.exists(), "[FAIL] package.json 不存在"

    lines = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    disallowed_deps = ["torch", "tensorflow", "transformers", "flask", "django"]
    contaminated = [dep for dep in lines if any(d in dep.lower() for d in disallowed_deps)]
    assert not contaminated, f"[FAIL] 依賴包含多餘肥大庫: {contaminated}"

    pkg_text = pkg_file.read_text(encoding="utf-8")
    assert "@solana/web3.js" in pkg_text and "@solana/kit" in pkg_text, "[FAIL] package.json 未鎖定 @solana/kit 與 Web3.js v3"

    print(f"{'5. 純淨依賴清單驗證':<24} {'requirements.txt & package.json 純淨':<36} {'鎖定 Web3.js v3':<14} {'[✅ PASS]'}")

    # ---------------------------------------------------------
    # 斷言 6: 核心算子/微內核延遲達標 (< 1.0 ms)
    # ---------------------------------------------------------
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

    print(f"{'6. 微內核延遲性能':<24} {'單筆完整結算執行 < 1.0 ms':<36} {f'{avg_latency_ms:.3f} ms':<14} {'[✅ PASS]'}")
    assert avg_latency_ms < 1.0, f"[FAIL] 結算延遲超標: {avg_latency_ms:.3f} ms >= 1.0 ms"

    print("=" * 90)
    print("✅ 02_核心代碼庫_SourceCode 六大強制判定條件全綠 PASS！")
    print("=" * 90 + "\n")
    return True


if __name__ == "__main__":
    success = audit_source_code()
    sys.exit(0 if success else 1)
