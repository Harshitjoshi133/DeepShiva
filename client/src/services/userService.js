/**
 * User Service - Manages current user information
 * For now, returns a fixed user ID of 10, but can be extended for proper authentication
 */

// Fixed user ID for the current implementation
const CURRENT_USER_ID = 10;

/**
 * Get the current user ID
 * @returns {string} The current user ID (always "10" for now)
 */
export const getCurrentUserId = () => {
  const userIdString = String(CURRENT_USER_ID);
  console.log('👤 Getting current user ID:', userIdString);
  return userIdString;
};

/**
 * Get current user information
 * @returns {Object} User information object
 */
export const getCurrentUser = () => {
  const userId = getCurrentUserId(); // This is now a string
  
  const userInfo = {
    id: userId, // String ID for API compatibility
    numericId: CURRENT_USER_ID, // Keep numeric ID for internal use
    username: `user_${userId}`,
    displayName: `User ${userId}`,
    email: `user${userId}@deepshiva.com`,
    preferredLanguage: 'en',
    isAuthenticated: true,
    role: 'user'
  };
  
  console.log('👤 Current user info:', userInfo);
  return userInfo;
};

/**
 * Check if user is authenticated
 * @returns {boolean} Always true for now
 */
export const isUserAuthenticated = () => {
  return true;
};

/**
 * Get user display name
 * @returns {string} User display name
 */
export const getUserDisplayName = () => {
  const user = getCurrentUser();
  return user.displayName;
};

/**
 * Get user preferred language
 * @returns {string} User preferred language
 */
export const getUserPreferredLanguage = () => {
  const user = getCurrentUser();
  return user.preferredLanguage;
};

// Export default object with all functions
export default {
  getCurrentUserId,
  getCurrentUser,
  isUserAuthenticated,
  getUserDisplayName,
  getUserPreferredLanguage
};