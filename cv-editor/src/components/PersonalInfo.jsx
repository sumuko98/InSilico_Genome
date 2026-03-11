export default function PersonalInfo({ data, onChange }) {
  const handle = (field) => (e) => onChange({ ...data, [field]: e.target.value });

  return (
    <section className="editor-section">
      <h2>Personal Information</h2>
      <div className="form-group">
        <label>Full Name</label>
        <input value={data.name} onChange={handle('name')} placeholder="Jane Doe" />
      </div>
      <div className="form-group">
        <label>Job Title</label>
        <input value={data.title} onChange={handle('title')} placeholder="Software Engineer" />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Email</label>
          <input value={data.email} onChange={handle('email')} placeholder="jane@example.com" type="email" />
        </div>
        <div className="form-group">
          <label>Phone</label>
          <input value={data.phone} onChange={handle('phone')} placeholder="+1 555 0100" />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Location</label>
          <input value={data.location} onChange={handle('location')} placeholder="City, Country" />
        </div>
        <div className="form-group">
          <label>Website / LinkedIn</label>
          <input value={data.website} onChange={handle('website')} placeholder="https://linkedin.com/in/jane" />
        </div>
      </div>
      <div className="form-group">
        <label>Summary</label>
        <textarea
          rows={4}
          value={data.summary}
          onChange={handle('summary')}
          placeholder="A brief professional summary..."
        />
      </div>
    </section>
  );
}
