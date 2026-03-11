export default function Education({ items, onChange }) {
  const update = (index, field, value) => {
    const updated = items.map((item, i) =>
      i === index ? { ...item, [field]: value } : item
    );
    onChange(updated);
  };

  const add = () =>
    onChange([
      ...items,
      { id: crypto.randomUUID(), institution: '', degree: '', field: '', startDate: '', endDate: '' },
    ]);

  const remove = (index) => onChange(items.filter((_, i) => i !== index));

  return (
    <section className="editor-section">
      <h2>Education</h2>
      {items.map((item, i) => (
        <div key={item.id} className="entry-card">
          <div className="entry-header">
            <span className="entry-number">#{i + 1}</span>
            <button className="btn-remove" onClick={() => remove(i)}>Remove</button>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Institution</label>
              <input value={item.institution} onChange={(e) => update(i, 'institution', e.target.value)} placeholder="MIT" />
            </div>
            <div className="form-group">
              <label>Degree</label>
              <input value={item.degree} onChange={(e) => update(i, 'degree', e.target.value)} placeholder="Bachelor of Science" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Field of Study</label>
              <input value={item.field} onChange={(e) => update(i, 'field', e.target.value)} placeholder="Computer Science" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <input value={item.startDate} onChange={(e) => update(i, 'startDate', e.target.value)} placeholder="Sep 2016" />
            </div>
            <div className="form-group">
              <label>End Date</label>
              <input value={item.endDate} onChange={(e) => update(i, 'endDate', e.target.value)} placeholder="Jun 2020" />
            </div>
          </div>
        </div>
      ))}
      <button className="btn-add" onClick={add}>+ Add Education</button>
    </section>
  );
}
