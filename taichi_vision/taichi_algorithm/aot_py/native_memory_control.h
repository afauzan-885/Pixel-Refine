#pragma once
#include <stdint.h>

// Additive C ABI v1. Initialize struct_size=sizeof(struct), abi_version=1.
// Byte counts are logical requested sizes. Unknown driver/physical/in-flight
// values use UINT64_MAX and their UNKNOWN flags; they are never measured zero.
enum {
  TI_AOT_MEMORY_PHYSICAL_UNKNOWN = 1,
  TI_AOT_MEMORY_IN_FLIGHT_UNKNOWN = 2,
  TI_AOT_MEMORY_COUNTER_SATURATED = 4,
  TI_AOT_MEMORY_UNRESOLVED_ALLOCATION = 8,
  TI_AOT_MEMORY_ACCOUNTING_ERROR = 16
};
typedef struct TiAotMemoryLimitsV1 {
  uint32_t struct_size, abi_version;
  uint64_t budget_bytes; // 0 unlimited; includes cache, quarantine, unresolved.
  uint64_t cache_max_bytes, cache_max_entries; // Both zero disables caching.
  uint64_t reserved[2]; // Must be zero.
} TiAotMemoryLimitsV1;

typedef struct TiAotMemorySnapshotV1 {
  uint32_t struct_size, abi_version;
  uint64_t flags;
  uint64_t budget_bytes, cache_max_bytes, cache_max_entries;
  uint64_t budget_charge_bytes, retained_bytes, pending_bytes, unresolved_bytes;
  uint64_t live_bytes, caller_bytes, private_staging_bytes, idle_cache_bytes;
  uint64_t mapped_bytes, quarantined_bytes, leased_private_bytes;
  uint64_t retained_count, unresolved_count, caller_count, private_staging_count;
  uint64_t idle_cache_count, mapped_count, quarantined_count, leased_private_count;
  uint64_t allocation_requests, allocation_requested_bytes_total, allocation_failures;
  uint64_t high_water_retained_bytes, high_water_budget_charge_bytes;
  uint64_t cache_hits, cache_misses;
  uint64_t physical_bytes, driver_budget_bytes, in_flight_bytes; // Unknown sentinel.
} TiAotMemorySnapshotV1;

typedef struct TiAotMemoryTrimV1 {
  uint32_t struct_size, abi_version;
  uint64_t valid; // Native sets 1 when partial/success counters were written.
  uint64_t freed_bytes, freed_entries, remaining_cache_bytes, remaining_cache_entries;
} TiAotMemoryTrimV1;

#ifdef __cplusplus
static_assert(sizeof(TiAotMemoryLimitsV1) == 48, "memory limits ABI layout");
static_assert(sizeof(TiAotMemorySnapshotV1) == 272, "memory snapshot ABI layout");
static_assert(sizeof(TiAotMemoryTrimV1) == 48, "memory trim ABI layout");
extern "C" {
#endif
// Return 1 on success, 0 on error; inspect get_last_engine_error(runtime).
int ti_aot_get_memory_snapshot(void *runtime, TiAotMemorySnapshotV1 *output);
int ti_aot_set_memory_limits(void *runtime, const TiAotMemoryLimitsV1 *limits);
// Reclaim only idle private staging. Targets are remaining cache caps; 0/0
// requests a full trim. Partial progress is reported even on native free error.
int ti_aot_trim_memory_cache(void *runtime, uint64_t target_bytes,
                             uint64_t target_entries, TiAotMemoryTrimV1 *output);
#ifdef __cplusplus
}
#endif
