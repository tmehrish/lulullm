import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = 'lulullm-production.up.railway.app';

function App() {
  const [user, setUser] = useState(null);
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Handle form input changes
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Handle authentication (sign up or sign in)
  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const endpoint = isSignUp ? '/signup' : '/signin';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const userData = await response.json();
      setUser(userData);
      setFormData({ username: '', password: '' });
      
      if (isSignUp) {
        setIsSignUp(false); // Switch to sign in view after successful sign up
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle sending chat messages
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setIsLoading(true);

    // Add user message to chat
    setChatMessages(prev => [...prev, { type: 'user', content: userMessage }]);

    try {
      // Send as query parameter
      const response = await fetch(`${API_BASE_URL}/invoke?user_input=${encodeURIComponent(userMessage)}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error:', errorText);
        throw new Error(`Server error: ${response.status}`);
      }

      const aiResponse = await response.text();
      
      // Add AI response to chat
      setChatMessages(prev => [...prev, { type: 'ai', content: aiResponse }]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message: ' + err.message);
      setChatMessages(prev => [...prev, { type: 'error', content: 'Failed to get response. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    setChatMessages([]);
    setCurrentMessage('');
    setError('');
  };

  // Render authentication form
  const renderAuthForm = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isSignUp ? 'Sign Up' : 'Sign In'}</h2>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleAuth}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>
          
          <button type="submit" disabled={isLoading} className="auth-button">
            {isLoading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Sign In')}
          </button>
        </form>
        
        <p className="auth-switch">
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button 
            type="button" 
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError('');
              setFormData({ username: '', password: '' });
            }}
            className="link-button"
          >
            {isSignUp ? 'Sign In' : 'Sign Up'}
          </button>
        </p>
      </div>
    </div>
  );

  // Render chat interface
  const renderChat = () => (
    <div className="chat-container">
      <div className="chat-header">
        <div className="user-info">
          <h3>Welcome, {user.username}!</h3>
          <span className="user-id">ID: {user.user_id}</span>
        </div>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
      
      <div className="chat-messages">
        {chatMessages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-content">
              <h2>Welcome to LuluLLM!</h2>
              <p>Your intelligent AI assistant designed to help you navigate life's challenges.</p>
              
              <div className="capabilities-section">
                <h3>Available Agents:</h3>
                <div className="capabilities-grid">
                  <div className="capability-item">
                    <div className="capability-icon">🧘</div>
                    <div className="capability-text">
                      <strong>Initial Stress Agent</strong>
                      <span>Immediate support for stress management and calming techniques</span>
                    </div>
                  </div>
                  
                  <div className="capability-item">
                    <div className="capability-icon">⚖️</div>
                    <div className="capability-text">
                      <strong>Decision Making Agent</strong>
                      <span>Structured approach to making important life decisions</span>
                    </div>
                  </div>
                  
                  <div className="capability-item">
                    <div className="capability-icon">🔍</div>
                    <div className="capability-text">
                      <strong>Indecision Analyst</strong>
                      <span>Break through analysis paralysis and find clarity</span>
                    </div>
                  </div>
                  
                  <div className="capability-item">
                    <div className="capability-icon">🌟</div>
                    <div className="capability-text">
                      <strong>Lifestyle Coach Agent</strong>
                      <span>Guidance for improving habits, wellness, and personal growth</span>
                    </div>
                  </div>
                  
                  <div className="capability-item">
                    <div className="capability-icon">💬</div>
                    <div className="capability-text">
                      <strong>General Chat Agent</strong>
                      <span>Open conversations on any topic you'd like to discuss</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <p className="start-prompt">What would you like to talk about today?</p>
            </div>
          </div>
        ) : (
          chatMessages.map((message, index) => (
            <div key={index} className={`message ${message.type}-message`}>
              <div className="message-content">
                {message.content.split('\n').map((line, lineIndex) => (
                  <React.Fragment key={lineIndex}>
                    {line}
                    {lineIndex < message.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message ai-message">
            <div className="message-content typing">
              AI is thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSendMessage} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="chat-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !currentMessage.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </form>
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );

  return (
    <div className="App">
      <header className="app-header">
        <h1>LuluLLM</h1>
      </header>
      
      <main className="app-main">
        {user ? renderChat() : renderAuthForm()}
      </main>
    </div>
  );
}

export default App;
