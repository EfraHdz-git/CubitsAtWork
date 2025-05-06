// src/App.tsx
import { useState, useEffect } from 'react';
import { CircuitResponse } from './services/api';
import Header from './components/Header';
import Layout from './components/Layout';
import InfoPanel from './components/InfoPanel';
import './App.css';

function App() {
  const [circuitData, setCircuitData] = useState<CircuitResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  
  // Check if viewport is mobile size
  useEffect(() => {
    const checkIsMobile = () => {
      const mobileView = window.innerWidth <= 768;
      setIsMobile(mobileView);
      setSidebarOpen(!mobileView); // Open on desktop, closed on mobile
    };
    
    // Initial check
    checkIsMobile();
    
    // Add event listener for window resize
    window.addEventListener('resize', checkIsMobile);
    
    // Clean up
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);
  
  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="app-wrapper">
      {/* Main header and content */}
      <div className={`app-content-section ${sidebarOpen && isMobile ? 'hidden-on-mobile' : ''}`}>
        <Header />
        
        <div className="content-wrapper">
          {/* Mobile sidebar toggle button - only shown on mobile */}
          {isMobile && (
            <button 
              className="sidebar-toggle" 
              onClick={toggleSidebar}
            >
              i
            </button>
          )}
          
          <main className="app-main">
            <Layout 
              circuitData={circuitData} 
              setCircuitData={setCircuitData} 
            />
          </main>
        </div>
      </div>
      
      {/* Sidebar with InfoPanel - remove icon circle on desktop */}
      <aside className={`app-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <InfoPanel showIcon={isMobile} />
      </aside>
    </div>
  );
}

export default App;