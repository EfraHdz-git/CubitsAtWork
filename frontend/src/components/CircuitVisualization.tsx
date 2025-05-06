// src/components/CircuitVisualization.tsx
import { useState, useRef, useEffect } from 'react';
import { 
  CircuitResponse, 
  getImageSource, 
  getImageMetadata 
} from '../services/api';
import '../assets/styles/components/CircuitVisualization.css';

interface Props {
  circuitData: CircuitResponse | null;
}

function CircuitVisualization({ circuitData }: Props) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [containerDimensions, setContainerDimensions] = useState({ width: 0, height: 0 });
  const [optimalZoom, setOptimalZoom] = useState(1);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  // Get the current visualization
  const getCurrentVisualization = () => {
    if (!circuitData?.visualization) return null;
    return circuitData.visualization.circuit_diagram;
  };

  // Update container dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (contentRef.current) {
        setContainerDimensions({
          width: contentRef.current.clientWidth,
          height: contentRef.current.clientHeight
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, [isFullScreen]);

  // Use metadata if available, otherwise use image dimensions from load event
  useEffect(() => {
    const currentVis = getCurrentVisualization();
    const metadata = getImageMetadata(currentVis);
    
    if (metadata && metadata.width && metadata.height) {
      // Use dimensions from metadata
      setImageDimensions({
        width: metadata.width,
        height: metadata.height
      });
    } else {
      // Reset dimensions to trigger re-calculation after image load
      setImageDimensions({ width: 0, height: 0 });
    }
  }, [circuitData]);

  // Calculate optimal zoom when image or container dimensions change
  useEffect(() => {
    if (imageDimensions.width > 0 && containerDimensions.width > 0) {
      const widthRatio = containerDimensions.width / imageDimensions.width;
      // For small circuits, don't zoom in too much - keep it natural size
      const newZoom = widthRatio < 1 ? widthRatio : 1;
      setOptimalZoom(newZoom);
      setZoomLevel(newZoom); // Auto-apply the optimal zoom
    }
  }, [imageDimensions, containerDimensions]);

  // Handle image load to get dimensions when metadata is not available
  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const currentVis = getCurrentVisualization();
    
    // Only use dimensions from image load if we don't have metadata
    if (!getImageMetadata(currentVis)) {
      const img = e.currentTarget;
      setImageDimensions({
        width: img.naturalWidth,
        height: img.naturalHeight
      });
    }
  };

  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen().catch(err => {
        console.log(err);
      });
      setIsFullScreen(true);
    } else {
      document.exitFullscreen();
      setIsFullScreen(false);
    }
  };

  // Monitor fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullScreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Fit to container
  const handleFitToContainer = () => {
    setZoomLevel(optimalZoom);
  };

// Handle download of the circuit image with white background
const handleDownloadImage = () => {
  const currentVis = getCurrentVisualization();
  if (!currentVis) return;
  
  const imgSrc = `data:image/png;base64,${getImageSource(currentVis)}`;
  
  // Create a canvas to draw the image with background
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();
  
  img.onload = () => {
    // Set canvas size to match image dimensions
    canvas.width = img.width;
    canvas.height = img.height;
    
    // Fill with white background
    if (ctx) {
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw the original image on top
      ctx.drawImage(img, 0, 0);
      
      // Convert to data URL
      const dataUrl = canvas.toDataURL('image/png');
      
      // Create download link
      const downloadLink = document.createElement('a');
      downloadLink.href = dataUrl;
      
      // Set a hardcoded filename for the download
      const filename = 'quantum-circuit';
      downloadLink.download = `${filename}.png`;
      
      // Trigger the download
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    }
  };
  
  // Set source to load the image
  img.src = imgSrc;
};

  // Render the circuit visualization
  const renderVisualization = () => {
    const currentVis = getCurrentVisualization();
    if (!currentVis) {
      return (
        <div className="circuit-vis-not-available">
          Circuit visualization not available
        </div>
      );
    }
    
    const imgSrc = `data:image/png;base64,${getImageSource(currentVis)}`;
    
    return (
      <div className="circuit-vis-image-container">
        <img 
          ref={imageRef}
          src={imgSrc}
          alt="Circuit Visualization"
          className="circuit-vis-image"
          style={{ transform: `scale(${zoomLevel})` }}
          onLoad={handleImageLoad}
        />
      </div>
    );
  };

  if (!circuitData) {
    return (
      <div className="card circuit-vis-container">
        <h2 className="circuit-vis-heading">Circuit Visualization</h2>
        <div className="circuit-vis-placeholder">
          Generate a circuit to see visualization
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`card circuit-vis-container ${isFullScreen ? 'fullscreen' : ''}`}>
      <div className="circuit-vis-header">
        <h2 className="circuit-vis-heading">Circuit Visualization</h2>
        
        <div className="circuit-vis-controls">
          <div className="zoom-controls">
            <button 
              className="zoom-button" 
              onClick={() => setZoomLevel(prev => Math.max(0.1, prev - 0.1))}
              title="Zoom out"
            >
              −
            </button>
            <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
            <button 
              className="zoom-button" 
              onClick={() => setZoomLevel(prev => prev + 0.1)}
              title="Zoom in"
            >
              +
            </button>
            <button
              className="zoom-fit-button"
              onClick={handleFitToContainer}
              title="Fit to view"
            >
              Fit
            </button>
          </div>
          
          <button 
            className="download-button" 
            onClick={handleDownloadImage}
            title="Download image"
            disabled={!getCurrentVisualization()}
          >
            Download
          </button>
          
          <button 
            className="fullscreen-button" 
            onClick={toggleFullScreen}
            title={isFullScreen ? "Exit full screen" : "Full screen"}
          >
            {isFullScreen ? "Exit Full Screen" : "Full Screen"}
          </button>
        </div>
      </div>
      
      <div className="circuit-vis-tabs">
        <button className="circuit-vis-tab active">
          Circuit View
        </button>
      </div>
      
      <div 
        ref={contentRef}
        className="circuit-vis-content circuit-mode"
      >
        {renderVisualization()}
      </div>
    </div>
  );
}

export default CircuitVisualization;