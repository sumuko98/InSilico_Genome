export default function CVPreview({ cv }) {
  const { personal, experience, education, skills } = cv;

  return (
    <div className="cv-preview">
      {/* Header */}
      <header className="preview-header">
        <h1>{personal.name || 'Your Name'}</h1>
        {personal.title && <p className="preview-title">{personal.title}</p>}
        <div className="preview-contact">
          {personal.email && <span>{personal.email}</span>}
          {personal.phone && <span>{personal.phone}</span>}
          {personal.location && <span>{personal.location}</span>}
          {personal.website && (
            <span>
              <a href={personal.website} target="_blank" rel="noreferrer">
                {personal.website}
              </a>
            </span>
          )}
        </div>
      </header>

      {/* Summary */}
      {personal.summary && (
        <section className="preview-section">
          <h2>Profile</h2>
          <p>{personal.summary}</p>
        </section>
      )}

      {/* Experience */}
      {experience.length > 0 && (
        <section className="preview-section">
          <h2>Work Experience</h2>
          {experience.map((exp) => (
            <div key={exp.id} className="preview-entry">
              <div className="preview-entry-header">
                <strong>{exp.role || 'Role'}</strong>
                <span className="preview-dates">
                  {exp.startDate} {exp.startDate || exp.endDate ? '–' : ''} {exp.endDate}
                </span>
              </div>
              {exp.company && <div className="preview-sub">{exp.company}</div>}
              {exp.description && <p>{exp.description}</p>}
            </div>
          ))}
        </section>
      )}

      {/* Education */}
      {education.length > 0 && (
        <section className="preview-section">
          <h2>Education</h2>
          {education.map((edu) => (
            <div key={edu.id} className="preview-entry">
              <div className="preview-entry-header">
                <strong>
                  {edu.degree}
                  {edu.degree && edu.field ? ' in ' : ''}
                  {edu.field}
                </strong>
                <span className="preview-dates">
                  {edu.startDate} {edu.startDate || edu.endDate ? '–' : ''} {edu.endDate}
                </span>
              </div>
              {edu.institution && <div className="preview-sub">{edu.institution}</div>}
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {skills.filter((s) => s.name).length > 0 && (
        <section className="preview-section">
          <h2>Skills</h2>
          <div className="preview-skills">
            {skills
              .filter((s) => s.name)
              .map((s) => (
                <span key={s.id} className="preview-skill-tag">
                  {s.name}
                </span>
              ))}
          </div>
        </section>
      )}
    </div>
  );
}
