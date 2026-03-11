export default function Experience({ items, onChange }) {
  const update = (index, field, value) => {
    const updated = items.map((item, i) =>
      i === index ? { ...item, [field]: value } : item
    );
    onChange(updated);
  };

  const add = () =>
    onChange([
      ...items,
      { id: crypto.randomUUID(), company: '', role: '', startDate: '', endDate: '', description: '' },
    ]);

  const remove = (index) => onChange(items.filter((_, i) => i !== index));

  return (
    <section className="editor-section">
      <h2>Work Experience</h2>
      {items.map((item, i) => (
        <div key={item.id} className="entry-card">
          <div className="entry-header">
            <span className="entry-number">#{i + 1}</span>
            <button className="btn-remove" onClick={() => remove(i)}>Remove</button>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Company</label>
              <input value={item.company} onChange={(e) => update(i, 'company', e.target.value)} placeholder="Acme Inc." />
            </div>
            <div className="form-group">
              <label>Role / Title</label>
              <input value={item.role} onChange={(e) => update(i, 'role', e.target.value)} placeholder="Senior Developer" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <input value={item.startDate} onChange={(e) => update(i, 'startDate', e.target.value)} placeholder="Jan 2020" />
            </div>
            <div className="form-group">
              <label>End Date</label>
              <input value={item.endDate} onChange={(e) => update(i, 'endDate', e.target.value)} placeholder="Present" />
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              rows={3}
              value={item.description}
              onChange={(e) => update(i, 'description', e.target.value)}
              placeholder="Key responsibilities and achievements..."
            />
          </div>
        </div>
      ))}
      <button className="btn-add" onClick={add}>+ Add Experience</button>
    </section>
  );
}
