import { useState } from 'react';
import PersonalInfo from './components/PersonalInfo';
import Experience from './components/Experience';
import Education from './components/Education';
import Skills from './components/Skills';
import CVPreview from './components/CVPreview';
import './App.css';

const TABS = ['Personal', 'Experience', 'Education', 'Skills'];

const initialCV = {
  personal: {
    name: '',
    title: '',
    email: '',
    phone: '',
    location: '',
    website: '',
    summary: '',
  },
  experience: [],
  education: [],
  skills: [],
};

function App() {
  const [cv, setCV] = useState(initialCV);
  const [activeTab, setActiveTab] = useState('Personal');

  const updatePersonal = (personal) => setCV((prev) => ({ ...prev, personal }));
  const updateExperience = (experience) => setCV((prev) => ({ ...prev, experience }));
  const updateEducation = (education) => setCV((prev) => ({ ...prev, education }));
  const updateSkills = (skills) => setCV((prev) => ({ ...prev, skills }));

  return (
    <div className="app">
      <header className="app-header">
        <h1>CV Editor</h1>
      </header>

      <div className="app-body">
        {/* Left panel – editor */}
        <div className="editor-panel">
          <nav className="tab-bar">
            {TABS.map((tab) => (
              <button
                key={tab}
                className={`tab-btn${activeTab === tab ? ' active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </nav>

          <div className="tab-content">
            {activeTab === 'Personal' && (
              <PersonalInfo data={cv.personal} onChange={updatePersonal} />
            )}
            {activeTab === 'Experience' && (
              <Experience items={cv.experience} onChange={updateExperience} />
            )}
            {activeTab === 'Education' && (
              <Education items={cv.education} onChange={updateEducation} />
            )}
            {activeTab === 'Skills' && (
              <Skills items={cv.skills} onChange={updateSkills} />
            )}
          </div>
        </div>

        {/* Right panel – live preview */}
        <div className="preview-panel">
          <CVPreview cv={cv} />
        </div>
      </div>
    </div>
  );
}

export default App;
