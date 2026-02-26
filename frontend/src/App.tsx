import React, { useEffect, useState } from "react";
import axios from "axios";

type ProductSource = {
  title?: string;
  name?: string;
  description?: string;
  price?: number;
  currency?: string;
  category?: string;
  brand?: string;
  [key: string]: unknown;
};

type Product = {
  id: string;
  score: number | null;
  ranking_score: number | null;
  source: ProductSource;
};

type SearchResponse = {
  total: number;
  items: Product[];
  took_ms: number;
  error?: string | null;
};

const initialResponse: SearchResponse = {
  total: 0,
  items: [],
  took_ms: 0,
  error: null
};

export const App: React.FC = () => {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SearchResponse>(initialResponse);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) {
      setData(initialResponse);
      setError(null);
      return;
    }

    const handler = setTimeout(() => {
      void performSearch();
    }, 300);

    return () => clearTimeout(handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, category, brand]);

  const performSearch = async () => {
    if (!query) return;

    try {
      setLoading(true);
      setError(null);

      const response = await axios.post<SearchResponse>("/api/search", {
        query,
        size: 20,
        filters: {
          category: category || null,
          brand: brand || null
        }
      });

      setData(response.data);
      if (response.data.error) {
        setError(response.data.error);
      }
    } catch (err) {
      setError("Search failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const showEmptyState = !query && !loading && data.items.length === 0;

  return (
    <div className="page">
      <header className="header">
        <h1>AI Semantic Product Search</h1>
        <p>
          Type a product query to see context-aware, ranked results powered by
          FastAPI, Elasticsearch, and a custom ranking pipeline.
        </p>
      </header>

      <section className="controls">
        <div className="search-row">
          <input
            className="search-input"
            placeholder="Search for 'wireless headphones', 'red running shoes', etc."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="search-button" onClick={performSearch}>
            Search
          </button>
        </div>

        <div className="filters">
          <div className="filter-field">
            <label>Category</label>
            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g. electronics, fashion"
            />
          </div>
          <div className="filter-field">
            <label>Brand</label>
            <input
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              placeholder="e.g. Nike, Apple"
            />
          </div>
        </div>
      </section>

      <section className="results-panel">
        <div className="results-meta">
          {loading && <span className="badge">Loading...</span>}
          {!loading && data.total > 0 && (
            <span className="badge">
              {data.total} results in {data.took_ms} ms
            </span>
          )}
          {error && <span className="badge badge-error">{error}</span>}
        </div>

        {showEmptyState && (
          <div className="empty-state">
            <h2>Start typing to search</h2>
            <p>
              This UI calls the FastAPI backend at <code>/api/search</code> and
              shows ranked Elasticsearch results in real time.
            </p>
          </div>
        )}

        {!showEmptyState && data.items.length > 0 && (
          <ul className="results-list">
            {data.items.map((item) => {
              const title = item.source.title || item.source.name || item.id;
              const description = item.source.description;

              return (
                <li key={item.id} className="result-card">
                  <div className="result-main">
                    <h3>{title}</h3>
                    {description && <p className="description">{description}</p>}
                    <div className="tags">
                      {item.source.category && (
                        <span className="tag">{item.source.category}</span>
                      )}
                      {item.source.brand && (
                        <span className="tag">{item.source.brand}</span>
                      )}
                    </div>
                  </div>

                  <div className="result-meta">
                    {item.source.price != null && (
                      <div className="price">
                        {item.source.currency || "$"}
                        {item.source.price}
                      </div>
                    )}
                    <div className="scores">
                      <span className="score-label">
                        Rank score:{" "}
                        {item.ranking_score != null
                          ? item.ranking_score.toFixed(3)
                          : "–"}
                      </span>
                      <span className="score-label secondary">
                        ES score:{" "}
                        {item.score != null ? item.score.toFixed(3) : "–"}
                      </span>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
};

