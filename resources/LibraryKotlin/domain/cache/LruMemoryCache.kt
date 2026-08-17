package org.pixelrefine.genericui.domain.cache

/**
 * Thread-safe LRU (Least Recently Used) Memory Cache generik.
 *
 * Mirror: `GlobalThumbnailCache` di `thumbnail_processor.py`
 */
class LruMemoryCache<K, V>(
    private val maxCapacity: Int = 100,
) {
    private val cacheMap = LinkedHashMap<K, V>(maxCapacity, 0.75f, true)
    private val lock = Any()

    fun get(key: K): V? {
        synchronized(lock) {
            return cacheMap[key]
        }
    }

    fun put(key: K, value: V): V? {
        synchronized(lock) {
            val previous = cacheMap.put(key, value)
            if (cacheMap.size > maxCapacity) {
                val eldestKey = cacheMap.keys.iterator().next()
                cacheMap.remove(eldestKey)
            }
            return previous
        }
    }

    fun remove(key: K): V? {
        synchronized(lock) {
            return cacheMap.remove(key)
        }
    }

    fun clear() {
        synchronized(lock) {
            cacheMap.clear()
        }
    }

    val size: Int
        get() = synchronized(lock) { cacheMap.size }

    fun containsKey(key: K): Boolean {
        synchronized(lock) {
            return cacheMap.containsKey(key)
        }
    }
}
