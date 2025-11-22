// Add these new functions before the analyze button handler

// Simple translation function fallback
function t(key) {
  const translations = {
    'badgeOffline': 'Offline'
  };
  return translations[key] || key;
}

// Instant Macros Preview - Show macros immediately
function showInstantMacrosPreview(record) {
  // Remove existing preview if any
  const existingPreview = document.getElementById('instantMacrosPreview');
  if (existingPreview) {
    existingPreview.remove();
  }
  
  const calories = record.calories || 0;
  const proteins = record.proteins || 0;
  const fats = record.fats || 0;
  const carbs = record.carbohydrates || 0;
  
  // Create preview element
  const preview = document.createElement('div');
  preview.id = 'instantMacrosPreview';
  preview.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
    max-width: 280px;
  `;
  
  preview.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
      <h4 style="margin:0;font-size:0.9rem;">
        Instant Macros
      </h4>
      <button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;color:white;cursor:pointer;padding:0;width:24px;height:24px;display:flex;align-items:center;justify-content:center;">&times;</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.85rem;">
      <div><strong>${calories}</strong> kcal</div>
      <div><strong>${proteins}g</strong> protein</div>
      <div><strong>${fats}g</strong> fat</div>
      <div><strong>${carbs}g</strong> carbs</div>
    </div>
  `;
  
  document.body.appendChild(preview);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (preview.parentElement) {
      preview.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => preview.remove(), 300);
    }
  }, 5000);
}

// Offline Indicator
function showOfflineIndicator() {
  const badge = document.querySelector('.badge-ghost');
  if (badge) {
    badge.style.background = 'rgba(255, 193, 7, 0.2)';
    badge.style.color = '#ff9800';
    badge.textContent = 'Offline Mode';
    
    // Reset after 3 seconds
    setTimeout(() => {
      badge.style.background = '';
      badge.style.color = '';
      badge.textContent = t('badgeOffline');
    }, 3000);
  }
}

// Add CSS animations
if (!document.getElementById('instantMacrosStyles')) {
  const style = document.createElement('style');
  style.id = 'instantMacrosStyles';
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }
  `;
  document.head.appendChild(style);
}

// Listen for online/offline events
window.addEventListener('online', () => {
  console.log('✅ Back online');
  const badge = document.querySelector('.badge-ghost');
  if (badge) {
    badge.textContent = t('badgeOffline');
  }
});

window.addEventListener('offline', () => {
  console.log('Gone offline');
  showOfflineIndicator();
});

// Global variable to store the current image data
let currentImageData = null;

// Convert image file to base64
function imageToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Handle file input change
document.addEventListener('DOMContentLoaded', () => {
  const foodImageInput = document.getElementById('foodImage');
  const uploadPreview = document.getElementById('uploadPreview');
  const analyzeBtn = document.getElementById('analyzeBtn');
  
  if (!foodImageInput || !uploadPreview || !analyzeBtn) {
    console.error('Required elements not found');
    return;
  }
  
  // Initially disable analyze button
  analyzeBtn.disabled = true;
  analyzeBtn.style.opacity = '0.6';
  analyzeBtn.style.cursor = 'not-allowed';
  
  // Handle file selection
  foodImageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    try {
      // Convert to base64
      currentImageData = await imageToBase64(file);
      
      // Show preview
      uploadPreview.innerHTML = `
        <img src="${currentImageData}" alt="Food preview" style="max-width: 100%; max-height: 300px; border-radius: 8px; margin-top: 1rem;">
        <p style="margin-top: 0.5rem; color: var(--text-secondary);">Image ready for analysis</p>
      `;
      
      // Enable analyze button
      analyzeBtn.disabled = false;
      analyzeBtn.style.opacity = '1';
      analyzeBtn.style.cursor = 'pointer';
      
      console.log('Image loaded successfully');
    } catch (error) {
      console.error('Error loading image:', error);
      uploadPreview.innerHTML = '<p style="color: red;">Error loading image. Please try again.</p>';
    }
  });
  
  // Handle analyze button click
  analyzeBtn.addEventListener('click', async () => {
    if (!currentImageData) {
      alert('Please select an image first');
      return;
    }
    
    // Disable button during analysis
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    analyzeBtn.style.opacity = '0.6';
    analyzeBtn.style.cursor = 'not-allowed';
    
    const resultSection = document.getElementById('predictionResult');
    resultSection.innerHTML = '<p>Analyzing your plate...</p>';
    resultSection.classList.remove('hidden');
    
    try {
      // First check if backend is reachable
      try {
        const healthCheck = await fetch('http://localhost:4000/health', {
          method: 'GET',
          timeout: 3000
        });
        if (!healthCheck.ok) {
          throw new Error('Backend health check failed');
        }
      } catch (healthError) {
        throw new Error('Cannot connect to backend server. Please make sure it is running on http://localhost:4000');
      }
      
      // Send to backend
      const response = await fetch('http://localhost:4000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'guest',
          image: currentImageData
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Display results
      displayResults(data, resultSection);
      
      // Show instant macros preview
      showInstantMacrosPreview(data);
      
    } catch (error) {
      console.error('Error analyzing image:', error);
      let errorMessage = error.message;
      
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Cannot connect to backend server. Please make sure:\n1. Backend is running (python backend.py)\n2. Server is on http://localhost:4000\n3. No firewall is blocking the connection';
      }
      
      resultSection.innerHTML = `
        <div style="color: red; padding: 1.5rem; background: rgba(255,0,0,0.1); border-radius: 8px; margin-top: 1rem;">
          <h3 style="margin-top: 0;">❌ Error</h3>
          <p style="white-space: pre-line;">${errorMessage}</p>
          <p style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.8;">
            To start the backend, open a terminal and run:<br>
            <code style="background: rgba(0,0,0,0.2); padding: 0.2rem 0.5rem; border-radius: 4px;">python backend.py</code>
          </p>
        </div>
      `;
    } finally {
      // Re-enable button
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = 'Analyze Plate';
      analyzeBtn.style.opacity = '1';
      analyzeBtn.style.cursor = 'pointer';
    }
  });
});

// Display analysis results
function displayResults(data, resultSection) {
  const foodItems = data.food_items || [];
  const foodItemsHTML = foodItems.length > 0
    ? `<div style="margin-bottom: 1rem;">
         <h4>Detected Food Items:</h4>
         <ul style="list-style: none; padding: 0;">
           ${foodItems.map(item => `<li style="padding: 0.5rem; background: rgba(255,255,255,0.1); margin: 0.5rem 0; border-radius: 4px;">
             <strong>${item.name}</strong> - ${item.quantity}
           </li>`).join('')}
         </ul>
       </div>`
    : '<p>No food items detected</p>';
  
  resultSection.innerHTML = `
    <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; margin-top: 1rem;">
      <h3 style="margin-top: 0;">Analysis Results</h3>
      ${foodItemsHTML}
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1.5rem;">
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
          <div style="font-size: 0.9rem; opacity: 0.8;">Calories</div>
          <div style="font-size: 2rem; font-weight: bold;">${data.calories || 0}</div>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
          <div style="font-size: 0.9rem; opacity: 0.8;">Proteins</div>
          <div style="font-size: 2rem; font-weight: bold;">${data.proteins || 0}g</div>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
          <div style="font-size: 0.9rem; opacity: 0.8;">Fats</div>
          <div style="font-size: 2rem; font-weight: bold;">${data.fats || 0}g</div>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
          <div style="font-size: 0.9rem; opacity: 0.8;">Carbs</div>
          <div style="font-size: 2rem; font-weight: bold;">${data.carbohydrates || 0}g</div>
        </div>
      </div>
      <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
        ${data.detected ? '✅ Food items detected' : '⚠️ No food items detected'}
      </p>
    </div>
  `;
}
