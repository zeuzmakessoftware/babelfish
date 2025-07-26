// Simple test to verify voice synthesis
async function testVoiceSynthesis() {
  console.log('Testing voice synthesis...');
  
  try {
    // Try the simple test endpoint first
    const response = await fetch('/api/voice/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const audioBlob = await response.blob();
    console.log('Audio blob received:', audioBlob.size, 'bytes');
    
    if (audioBlob.size === 0) {
      throw new Error('Audio blob is empty');
    }
    
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    audio.onloadstart = () => console.log('Audio loading...');
    audio.oncanplay = () => console.log('Audio ready to play');
    audio.onplay = () => console.log('Audio playing...');
    audio.onended = () => {
      console.log('Audio finished playing');
      URL.revokeObjectURL(audioUrl);
    };
    audio.onerror = (error) => {
      console.error('Audio error:', error);
      URL.revokeObjectURL(audioUrl);
    };

    try {
      await audio.play();
      console.log('✅ Voice synthesis test successful!');
    } catch (playError) {
      if (playError.name === 'NotAllowedError') {
        console.log('⚠️  Audio autoplay blocked. Click the page to enable audio.');
        console.log('✅ Voice synthesis is working - just need user interaction to play audio.');
        
        // Set up click listener to play audio
        const playOnClick = () => {
          audio.play().then(() => {
            console.log('✅ Audio playing after user interaction!');
            document.removeEventListener('click', playOnClick);
          }).catch(e => {
            console.error('❌ Still cannot play audio:', e);
          });
        };
        
        document.addEventListener('click', playOnClick, { once: true });
      } else {
        throw playError;
      }
    }
    
  } catch (error) {
    console.error('❌ Voice synthesis test failed:', error);
    
    // Try the full synthesis endpoint as fallback
    console.log('Trying full synthesis endpoint...');
    try {
      const response = await fetch('/api/voice/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Hello, this is a test.',
          voice_style: 'professional_female',
          speed: 1.0
        }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        await audio.play();
        console.log('✅ Full synthesis test successful!');
      }
    } catch (fallbackError) {
      console.error('❌ Full synthesis also failed:', fallbackError);
    }
  }
}

// Test backend health
async function testBackendHealth() {
  console.log('Testing backend health...');
  
  try {
    const response = await fetch('/');
    const data = await response.json();
    console.log('Backend health:', data);
    return true;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}

// Run tests
async function runTests() {
  console.log('🚀 Running voice tests...');
  
  const backendHealthy = await testBackendHealth();
  if (backendHealthy) {
    await testVoiceSynthesis();
  } else {
    console.log('❌ Backend not available. Make sure to start the backend with: cd backend && python main.py');
  }
}

// Export for use in browser console
window.testVoice = runTests; 