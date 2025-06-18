// src/utils/authFetch.js

const authFetch = async (url, options = {}) => {
    const token = localStorage.getItem("token");
  
    const headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  
    const config = {
      ...options,
      headers,
    };
  
    const response = await fetch(url, config);
  
    if (response.status === 401) {
      alert("Sua sessão expirou. Faça login novamente.");
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  
    return response;
  };
  
  export default authFetch;
  