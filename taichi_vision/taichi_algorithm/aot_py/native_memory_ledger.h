#pragma once
#include <cstdint>
#include <limits>

namespace pixel_refine {

// Logical requested-byte accounting, not physical driver/VRAM telemetry.
// Caller serializes transitions with the engine lifetime lock.
struct MemoryLedger {
  uint64_t retained = 0, pending = 0, unresolved = 0, charge = 0;
  uint64_t retained_count = 0, unresolved_count = 0;
  uint64_t requested_total = 0, requests = 0, failures = 0;
  uint64_t high_retained = 0, high_charge = 0;
  bool saturated = false, invariant_error = false;

  void accumulate(uint64_t &value, uint64_t amount) noexcept {
    if (amount > (std::numeric_limits<uint64_t>::max)() - value) {
      value = (std::numeric_limits<uint64_t>::max)();
      saturated = true;
    } else value += amount;
  }
  bool reserve(uint64_t bytes, uint64_t budget) noexcept {
    accumulate(requests, 1);
    accumulate(requested_total, bytes);
    const uint64_t max = (std::numeric_limits<uint64_t>::max)();
    if (invariant_error || !bytes || bytes > max - charge || (budget && (charge > budget || bytes > budget - charge))) {
      accumulate(failures, 1);
      return false;
    }
    charge += bytes;
    pending += bytes; // pending <= charge, so this addition cannot overflow.
    if (charge > high_charge) high_charge = charge;
    return true;
  }
  void cancel(uint64_t bytes) noexcept {
    if (bytes > pending || bytes > charge) { invariant_error = true; return; }
    pending -= bytes;
    charge -= bytes;
    accumulate(failures, 1);
  }
  void commit(uint64_t bytes) noexcept {
    if (bytes > pending) { invariant_error = true; return; }
    pending -= bytes;
    retained += bytes; // retained + unresolved + pending == charge.
    ++retained_count;  // Every allocation is nonzero and retained <= UINT64_MAX.
    if (retained > high_retained) high_retained = retained;
  }
  void uncertain(uint64_t bytes) noexcept {
    if (bytes > pending) { invariant_error = true; return; }
    pending -= bytes;
    unresolved += bytes;
    ++unresolved_count;
    accumulate(failures, 1);
  }
  void release(uint64_t bytes) noexcept {
    if (bytes > retained || bytes > charge || !retained_count) {
      invariant_error = true;
      return; // Never wrap or undercharge if an internal invariant is broken.
    }
    retained -= bytes;
    charge -= bytes;
    --retained_count;
  }
};

struct MemoryReservation {
  MemoryLedger &ledger;
  uint64_t bytes;
  bool entered_native = false, committed = false;
  MemoryReservation(MemoryLedger &owner, uint64_t size) : ledger(owner), bytes(size) {}
  MemoryReservation(const MemoryReservation &) = delete;
  MemoryReservation &operator=(const MemoryReservation &) = delete;
  ~MemoryReservation() noexcept {
    if (!committed) {
      if (entered_native) ledger.uncertain(bytes);
      else ledger.cancel(bytes);
    }
  }
  void commit() noexcept { ledger.commit(bytes); committed = true; }
};

inline bool cache_fits(uint64_t bytes, uint64_t entries, uint64_t capacity,
                       uint64_t max_bytes, uint64_t max_entries) noexcept {
  return max_bytes && max_entries && entries < max_entries && bytes <= max_bytes &&
         capacity <= max_bytes - bytes;
}

template <typename Record>
bool idle_cache_eligible(const Record &record) noexcept {
  return record.private_staging && record.cached && record.complete &&
         !record.leased && !record.mapped && !record.release_failed;
}

}  // namespace pixel_refine
