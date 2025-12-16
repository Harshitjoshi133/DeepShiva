/**
 * MapmyIndia (Mappls) Service
 * Handles REST API calls for the Mappls mapping service
 */

const API_BASE = '/api/v1/mappls';

class MapplsService {
  constructor() {
    this.accessToken = null;
  }

  /**
   * Get a valid access token from the server
   * @returns {Promise<string>} Access token
   */
  async getAccessToken() {
    try {
      // Always fetch from server (token is static from .env)
      if (this.accessToken) {
        return this.accessToken;
      }

      console.log('Fetching Mappls access token...');
      const response = await fetch(`${API_BASE}/token`);
      
      if (!response.ok) {
        throw new Error(`Failed to get access token: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.access_token) {
        throw new Error('No access token in response');
      }

      // Cache the token (it's static from .env)
      this.accessToken = data.access_token;

      console.log('Mappls access token obtained successfully');
      return this.accessToken;

    } catch (error) {
      console.error('Error getting Mappls access token:', error);
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }

  /**
   * Search for places using autosuggest
   * @param {string} query - Search query
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Autosuggest results
   */
  async autoSuggest(query, options = {}) {
    try {
      const params = new URLSearchParams({
        query,
        region: options.region || 'IND',
        tokenizeAddress: options.tokenizeAddress !== false ? 'true' : 'false'
      });

      if (options.location) params.append('location', options.location);
      if (options.pod) params.append('pod', options.pod);
      if (options.filter) params.append('filter', options.filter);

      const response = await fetch(`${API_BASE}/autosuggest?${params}`);
      
      if (!response.ok) {
        throw new Error(`Autosuggest request failed: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error in autosuggest:', error);
      throw new Error(`Autosuggest failed: ${error.message}`);
    }
  }

  /**
   * Geocode an address
   * @param {string} address - Address to geocode
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Geocoding results
   */
  async geocode(address, options = {}) {
    try {
      const params = new URLSearchParams({
        address,
        itemCount: options.itemCount || 1,
        bias: options.bias || 0
      });

      const response = await fetch(`${API_BASE}/geocode?${params}`);
      
      if (!response.ok) {
        throw new Error(`Geocode request failed: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error in geocode:', error);
      throw new Error(`Geocode failed: ${error.message}`);
    }
  }

  /**
   * Get route between two points
   * @param {string} start - Start coordinates as "lat,lng"
   * @param {string} end - End coordinates as "lat,lng"
   * @param {Object} options - Route options
   * @returns {Promise<Object>} Route data
   */
  async getRoute(start, end, options = {}) {
    try {
      const params = new URLSearchParams({
        start,
        end,
        profile: options.profile || 'driving',
        alternatives: options.alternatives ? 'true' : 'false',
        steps: options.steps !== false ? 'true' : 'false',
        overview: options.overview || 'full'
      });

      const response = await fetch(`${API_BASE}/route?${params}`);
      
      if (!response.ok) {
        throw new Error(`Route request failed: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error getting route:', error);
      throw new Error(`Route request failed: ${error.message}`);
    }
  }

  /**
   * Get traffic data for a specific area
   * @param {string} bbox - Bounding box coordinates
   * @param {number} zoom - Zoom level
   * @returns {Promise<Object>} Traffic data
   */
  async getTrafficData(bbox, zoom = 10) {
    try {
      const params = new URLSearchParams({
        zoom: zoom.toString()
      });
      
      if (bbox) params.append('bbox', bbox);

      const response = await fetch(`${API_BASE}/traffic?${params}`);
      
      if (!response.ok) {
        throw new Error(`Traffic API request failed: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error getting traffic data:', error);
      throw new Error(`Traffic data request failed: ${error.message}`);
    }
  }

  /**
   * Check if Mappls service is healthy
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE}/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking Mappls health:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }

  /**
   * Clear cached token (useful for testing or logout)
   */
  clearToken() {
    this.accessToken = null;
  }
}

// Export singleton instance
export default new MapplsService();