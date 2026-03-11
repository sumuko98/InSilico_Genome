export default function Skills({ items, onChange }) {
  const update = (index, value) => {
    const updated = items.map((item, i) => (i === index ? { ...item, name: value } : item));
    onChange(updated);
  };

  const add = () => onChange([...items, { id: crypto.randomUUID(), name: '' }]);
  const remove = (index) => onChange(items.filter((_, i) => i !== index));

  return (
    <section className="editor-section">
      <h2>Skills</h2>
      <div className="skills-grid">
        {items.map((item, i) => (
          <div key={item.id} className="skill-item">
            <input
              value={item.name}
              onChange={(e) => update(i, e.target.value)}
              placeholder="e.g. JavaScript"
            />
            <button className="btn-remove-inline" onClick={() => remove(i)}>✕</button>
          </div>
        ))}
      </div>
      <button className="btn-add" onClick={add}>+ Add Skill</button>
    </section>
  );
}
