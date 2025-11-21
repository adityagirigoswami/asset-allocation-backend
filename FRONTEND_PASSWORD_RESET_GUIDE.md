# Frontend Password Reset Integration Guide

## Overview
This guide explains how to integrate the password reset functionality in your frontend application.

## Password Reset Flow

1. **Request Reset** → User enters email and requests password reset
2. **Email Sent** → Backend sends email with reset link containing token
3. **Reset Page** → User clicks link, lands on frontend reset page with token
4. **Submit New Password** → User enters new password and submits to backend

---

## API Endpoints

### 1. Request Password Reset
**Endpoint:** `POST /auth/password/reset-request`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success - 200):**
```json
{
  "detail": "If the email exists, a reset link will be sent."
}
```

**Note:** Always returns success message (even if email doesn't exist) to prevent email enumeration attacks.

---

### 2. Confirm Password Reset
**Endpoint:** `POST /auth/password/reset`

**Request Body:**
```json
{
  "token": "uuid-token-from-email-link",
  "new_password": "NewSecurePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "detail": "Password reset successful"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired token
- `404 Not Found` - User not found
- `422 Unprocessable Entity` - Validation errors (missing fields, invalid password format)

---

## Frontend Implementation

### Step 1: Create "Forgot Password" Page

Create a component/page where users can enter their email to request a password reset.

**Example: `ForgotPassword.jsx` (React)**
```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/password/reset-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.detail || 'If the email exists, a reset link will be sent.');
      } else {
        setError(data.error || 'Failed to send reset email. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <h2>Forgot Password</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="Enter your email"
          />
        </div>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>
    </div>
  );
};

export default ForgotPassword;
```

---

### Step 2: Create "Reset Password" Page

Create a component/page that accepts the token from the URL query parameter and allows users to set a new password.

**Example: `ResetPassword.jsx` (React)**
```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Check if token exists in URL
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Client-side validation
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/password/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Redirect to login page after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        // Handle error response format
        setError(data.error || data.detail || 'Failed to reset password. The link may have expired.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="reset-password-container">
        <h2>Invalid Reset Link</h2>
        <p>This reset link is invalid. Please request a new password reset.</p>
        <button onClick={() => navigate('/forgot-password')}>
          Request New Reset Link
        </button>
      </div>
    );
  }

  if (success) {
    return (
      <div className="reset-password-container">
        <h2>Password Reset Successful!</h2>
        <p>Your password has been reset successfully. Redirecting to login...</p>
      </div>
    );
  }

  return (
    <div className="reset-password-container">
      <h2>Reset Password</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="password">New Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter new password"
            minLength={8}
          />
        </div>
        <div>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            placeholder="Confirm new password"
            minLength={8}
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={loading || !token}>
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
      <p className="help-text">
        Password must be at least 8 characters long.
      </p>
    </div>
  );
};

export default ResetPassword;
```

---

### Step 3: Setup Routes

Add routes for both pages in your router configuration.

**Example: `App.jsx` or Router Setup**
```jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Login from './pages/Login';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        {/* ... other routes */}
      </Routes>
    </Router>
  );
}

export default App;
```

---

### Step 4: Add Link to Login Page

Add a "Forgot Password?" link on your login page.

**Example: Add to `Login.jsx`**
```jsx
import { Link } from 'react-router-dom';

// Inside your Login component JSX
<div className="login-form">
  {/* ... email and password inputs */}
  
  <div className="forgot-password-link">
    <Link to="/forgot-password">Forgot Password?</Link>
  </div>
  
  <button type="submit">Login</button>
</div>
```

---

## Environment Configuration

### Frontend `.env` File

Make sure your frontend has the API URL configured:

```env
REACT_APP_API_URL=http://localhost:8000
# or for production:
# REACT_APP_API_URL=https://your-api-domain.com
```

### Backend `.env` File

Ensure your backend has the frontend reset URL configured:

```env
FRONTEND_RESET_URL=http://localhost:3000/reset-password
# or for production:
# FRONTEND_RESET_URL=https://your-frontend-domain.com/reset-password
```

---

## Testing the Flow

### 1. Test Request Password Reset
1. Navigate to `/forgot-password`
2. Enter a valid email address
3. Click "Send Reset Link"
4. Check your email inbox for the reset link

### 2. Test Reset Password
1. Click the reset link from the email (should open `/reset-password?token=...`)
2. Enter a new password
3. Confirm the password
4. Click "Reset Password"
5. Should redirect to login page

### 3. Test Error Cases
- Invalid/expired token → Should show error message
- Missing token in URL → Should show "Invalid reset link"
- Password mismatch → Should show client-side validation error
- Token already used → Should show error (backend validates this)

---

## Error Handling

The backend returns standardized error responses:

```json
{
  "status_code": 400,
  "error": "Invalid or expired token",
  "success": false
}
```

Always check for the `error` key in the response and display it to the user.

---

## Security Considerations

1. **Token Expiration**: Tokens expire after 1 hour (configurable in backend)
2. **One-Time Use**: Tokens are marked as used after successful reset
3. **Email Enumeration Prevention**: Backend always returns success message
4. **HTTPS in Production**: Always use HTTPS in production for secure token transmission

---

## Alternative: Vanilla JavaScript Example

If you're not using React, here's a vanilla JS example:

**`reset-password.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
</head>
<body>
    <div id="reset-container">
        <h2>Reset Password</h2>
        <form id="reset-form">
            <div>
                <label>New Password:</label>
                <input type="password" id="password" required minlength="8">
            </div>
            <div>
                <label>Confirm Password:</label>
                <input type="password" id="confirmPassword" required minlength="8">
            </div>
            <div id="error-message" style="color: red;"></div>
            <div id="success-message" style="color: green;"></div>
            <button type="submit">Reset Password</button>
        </form>
    </div>

    <script>
        // Get token from URL
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (!token) {
            document.getElementById('error-message').textContent = 
                'Invalid reset link. Please request a new password reset.';
            document.getElementById('reset-form').style.display = 'none';
        }

        document.getElementById('reset-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const errorDiv = document.getElementById('error-message');
            const successDiv = document.getElementById('success-message');
            
            errorDiv.textContent = '';
            successDiv.textContent = '';

            if (password !== confirmPassword) {
                errorDiv.textContent = 'Passwords do not match.';
                return;
            }

            try {
                const response = await fetch('http://localhost:8000/auth/password/reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: token,
                        new_password: password,
                    }),
                });

                const data = await response.json();

                if (response.ok) {
                    successDiv.textContent = 'Password reset successful! Redirecting to login...';
                    setTimeout(() => {
                        window.location.href = '/login.html';
                    }, 3000);
                } else {
                    errorDiv.textContent = data.error || 'Failed to reset password.';
                }
            } catch (err) {
                errorDiv.textContent = 'Network error. Please try again.';
            }
        });
    </script>
</body>
</html>
```

---

## Summary

1. **Request Reset**: User enters email → Call `POST /auth/password/reset-request`
2. **Email Link**: Backend sends email with `FRONTEND_RESET_URL?token={token}`
3. **Reset Page**: Frontend extracts token from URL → User enters new password
4. **Submit**: Call `POST /auth/password/reset` with token and new password
5. **Success**: Redirect to login page

Make sure both frontend and backend URLs are properly configured in your `.env` files!

