// Deferred C++ tests for the actual pure ledger/cache-cap helpers used by the
// bridge. Not compiled or executed during the no-compilation source session.
#include "../native_memory_ledger.h"
#include <stdexcept>

static void check(bool condition) {
  if (!condition) throw std::runtime_error("native memory ledger regression failed");
}
#include <limits>

int main() {
  using pixel_refine::MemoryLedger;
  using pixel_refine::MemoryReservation;
  const auto max = (std::numeric_limits<uint64_t>::max)();
  MemoryLedger ledger;
  check(ledger.reserve(16, 32));
  { MemoryReservation reservation(ledger, 16); } // Host bookkeeping failed before native.
  check(ledger.charge == 0 && ledger.pending == 0 && ledger.failures == 1);
  check(ledger.reserve(16, 32));
  { MemoryReservation reservation(ledger, 16); reservation.entered_native = true; reservation.commit(); }
  check(ledger.retained == 16 && ledger.charge == 16 && ledger.retained_count == 1);
  check(!ledger.reserve(17, 32)); // Includes retained caller/private/cache/quarantine bytes.
  check(ledger.charge == 16 && ledger.pending == 0);
  check(ledger.reserve(16, 32));
  { MemoryReservation reservation(ledger, 16); reservation.entered_native = true; }
  check(ledger.unresolved == 16 && ledger.charge == 32 && ledger.unresolved_count == 1);
  check(!ledger.reserve(1, 32)); // Unknown no-handle outcome stays budget charged.
  ledger.release(16);
  check(ledger.retained == 0 && ledger.charge == 16 && ledger.unresolved == 16);
  check(ledger.high_retained == 16 && ledger.high_charge == 32);
  MemoryLedger overflow;
  check(overflow.reserve(max, 0));
  { MemoryReservation reservation(overflow, max); reservation.entered_native = true; reservation.commit(); }
  check(!overflow.reserve(1, 0)); // Unlimited policy does not permit uint64 wrap.
  check(overflow.charge == max && overflow.saturated);
  overflow.release(max);
  check(overflow.charge == 0 && overflow.retained_count == 0);
  overflow.release(1); // Fail closed on underflow; no wrap/negative logical usage.
  check(overflow.invariant_error && !overflow.reserve(1, 0));
  check(!pixel_refine::cache_fits(0, 0, 16, 0, 0));
  check(!pixel_refine::cache_fits(0, 0, 16, 32, 0));
  check(pixel_refine::cache_fits(16, 1, 16, 32, 2));
  check(!pixel_refine::cache_fits(16, 2, 1, 32, 2));
  check(!pixel_refine::cache_fits(16, 1, 17, 32, 2));
  check(!pixel_refine::cache_fits(max, 0, 1, max, 2));
  struct Record {
    bool private_staging = true, cached = true, complete = true;
    bool leased = false, mapped = false, release_failed = false;
  } record;
  check(pixel_refine::idle_cache_eligible(record));
  record.leased = true;
  check(!pixel_refine::idle_cache_eligible(record));
  record.leased = false; record.mapped = true;
  check(!pixel_refine::idle_cache_eligible(record));
  record.mapped = false; record.release_failed = true;
  check(!pixel_refine::idle_cache_eligible(record));
  record.release_failed = false; record.complete = false;
  check(!pixel_refine::idle_cache_eligible(record));
  record.complete = true; record.private_staging = false;
  check(!pixel_refine::idle_cache_eligible(record));
}
