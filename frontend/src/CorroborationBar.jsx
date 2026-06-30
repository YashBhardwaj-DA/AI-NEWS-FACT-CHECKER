// The signature element: a literal tick-mark bar where each tick represents
// a distinct source. Filled ticks = sources actually corroborating this story.
// Makes "how verified is this" a spatial read, not just a number buried in text.
export default function CorroborationBar({ sourceCount, maxTicks = 4 }) {
  const ticks = Array.from({ length: maxTicks }, (_, i) => i < sourceCount);

  return (
    <div className="corrobar" title={`${sourceCount} independent source(s) reporting this`}>
      {ticks.map((filled, i) => (
        <span key={i} className={`tick ${filled ? "filled" : ""}`} />
      ))}
      <span className="corrobar-label">
        {sourceCount} source{sourceCount === 1 ? "" : "s"}
      </span>
    </div>
  );
}
