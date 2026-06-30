import { useEffect, useState } from "react";
import { fetchFeed } from "./api";
import CorroborationBar from "./CorroborationBar";

export default function Feed() {
  const [clusters, setClusters] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFeed()
      .then((data) => setClusters(data.clusters))
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return <div className="error-state">Couldn't load the feed right now — {error}</div>;
  }

  if (!clusters) {
    return <div className="loading-state">Pulling latest headlines…</div>;
  }

  if (clusters.length === 0) {
    return <div className="empty-state">No stories found. Try refreshing shortly.</div>;
  }

  return (
    <div>
      {clusters.map((cluster, i) => (
        <article className="story-card" key={i}>
          <div className="meta-row">
            <span className="category">{cluster.articles[0].category}</span>
            <CorroborationBar sourceCount={cluster.source_count} />
          </div>
          <h2>
            <a href={cluster.articles[0].link} target="_blank" rel="noreferrer">
              {cluster.representative_title}
            </a>
          </h2>
          <div className="sources-list">
            {[...new Set(cluster.articles.map((a) => a.source))].map((s) => (
              <span className="source-chip" key={s}>
                {s}
              </span>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
