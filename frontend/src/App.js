import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chat.css';

const Chat = () => {
  const [clientId] = useState(() => Date.now().toString());
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const ws = useRef(null);
  const messagesEndRef = useRef(null);

  // Function to fetch the last five messages
  const fetchLastMessages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/last_messages');
      setMessages(response.data); // Assuming the response data is already in the correct order
    } catch (error) {
      console.error('Error fetching last messages:', error);
    }
  };

  // Function to scroll to the bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // Fetch the last messages when the component mounts
    fetchLastMessages();

    // Establish the WebSocket connection and set up event handlers
    ws.current = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const receivedMessage = JSON.parse(event.data);
      if (receivedMessage) {
        const isOwnMessage = receivedMessage.client_id === clientId;
        setMessages((prevMessages) => [...prevMessages, { ...receivedMessage, isOwnMessage }]);
      }
    };

    ws.current.onclose = () => console.log('WebSocket connection closed');
    ws.current.onerror = (error) => console.error('WebSocket error:', error);

    // Scroll to the bottom whenever messages are updated
    scrollToBottom();

    // Clean up the WebSocket connection when the component unmounts
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [clientId]);

  // Scroll to the bottom whenever messages change
  useEffect(scrollToBottom, [messages]);

  // Function to send a new message
  const sendMessage = (event) => {
    event.preventDefault();
    if (ws.current && ws.current.readyState === WebSocket.OPEN && newMessage) {
      const messagePayload = {
        sender: `User${clientId}`,  // This would ideally be the actual user's username or ID
        message: newMessage,
        isOwnMessage: true
      };
      ws.current.send(JSON.stringify(messagePayload));
      setNewMessage('');
    }
  };

  return (
    <div className="container">
      <div className="chat-window">
        <h1 className="chat-header">WebSocket Chat</h1>
        <h2>Your ID: {clientId}</h2>
        <ul className="messages-list">
          {messages.map((msg, index) => (
            <li key={index} className={`message-item ${msg.isOwnMessage ? 'my-message' : ''}`}>
              <span className="message-sender">{msg.sender || 'Anonymous'}</span> {/* Display sender */}
              {msg.content || msg.message}
            </li>
          ))}
          {/* Empty div to scroll into view */}
          <div ref={messagesEndRef} />
        </ul>
        <form onSubmit={sendMessage} className="message-form">
          <input
            className="message-input"
            type="text"
            id="messageText"
            autoComplete="off"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <button type="submit" className="send-button">Send</button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
