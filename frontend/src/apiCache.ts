class ApiCache<T> {
  private cache = new Map<string, T>();
  private keys: string[] = [];
  private limit: number;

  constructor(limit = 20) {
    this.limit = limit;
  }

  get(key: string): T | undefined {
    return this.cache.get(key);
  }

  set(key: string, value: T) {
    if (this.cache.has(key)) {
      // Move to end of keys to mark as most recently used
      this.keys = this.keys.filter((k) => k !== key);
    } else if (this.keys.length >= this.limit) {
      const oldestKey = this.keys.shift();
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
    this.cache.set(key, value);
    this.keys.push(key);
  }

  clear() {
    this.cache.clear();
    this.keys = [];
  }
}

// Define specific types for the results being cached
type PhiloRowItem = [number, string];
interface ResponseData {
  selectId: number;
  error: string;
  wtprefix: string;
  nocache: number;
  container: string;
  requestTime: number;
  page: number;
  lastPage: number;
  lastPageUp: number;
  query: string;
  arrOptions: Array<PhiloRowItem>;
}

export const searchCache = new ApiCache<ResponseData>(20);
export const rangeCache = new ApiCache<ResponseData>(20);
export const definitionCache = new ApiCache<string>(20);
