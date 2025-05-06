// src/components/Header.tsx
import { useState } from 'react';
import '../assets/styles/components/Header.css';

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <div className="header-logo">
            <img src="/logo.svg" alt="CubitsAtWork" className="logo-image" />
            <div className="logo-text">
              <h1 className="header-title">CubitsAtWork</h1>
              <div className="header-subtitle">Quantum Circuit Generator</div>
            </div>
          </div>
        </div>
        
        <div className="header-nav">
          {/* Nav links commented out in original */}
        </div>
        
        <div className="header-actions">
          {/* IBM Cloud Badge */}
          <div className="cloud-badge">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg" alt="IBM Cloud" width="20" />
            <span>Powered by IBM Cloud</span>
          </div>
          
          {/* Mobile menu button */}
          <button 
            className="mobile-menu-button"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isMenuOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </>
              ) : (
                <>
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </>
              )}
            </svg>
          </button>
        </div>
      </div>
      
      {/* Mobile navigation - commented out in original */}
    </header>
  );
}

export default Header;