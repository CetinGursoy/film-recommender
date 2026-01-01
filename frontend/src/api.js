// frontend/src/api.js

// API BASE URL
let API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  API_URL = "";
}

// Sondaki slash'ı temizle
API_URL = API_URL.replace(/\/$/, "");

export async function apiFetch(path, { method = "GET", body = null, token = null } = {}) {
  if (!path.startsWith("/")) path = "/" + path;

  const url = API_URL + path;

  const headers = { "Content-Type": "application/json" };

  const finalToken = token || localStorage.getItem("token") || sessionStorage.getItem("token"); // 🔥 Check passed token, then local, then session
  if (finalToken) headers["Authorization"] = `Bearer ${finalToken}`;

  let res;
  try {
    // Add 30 second timeout for slow backend operations
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
  } catch (err) {
    // Ağ veya bağlantı hatası (Backend kapalı veya timeout)
    if (err.name === 'AbortError') {
      throw { status: 0, detail: "İstek zaman aşımına uğradı. Lütfen tekrar deneyin." };
    }
    throw { status: 0, detail: `Bağlantı hatası: ${err.message}` };
  }

  const text = await res.text();
  let data = null;
  try {
    // Yanıt gövdesi varsa JSON olarak parse et
    data = text ? JSON.parse(text) : null;
  } catch {
    // JSON değilse veya boşsa, metin olarak kalabilir.
    data = text;
  }

  if (!res.ok) {
    // Backend'den 4xx veya 5xx hata kodu gelirse
    let detailMessage = "API hatası";
    if (typeof data === 'object' && data?.detail) {
      detailMessage = data.detail;
    } else if (typeof data === 'string' && data) {
      // Hata gövdesi bir string ise
      detailMessage = data;
    }

    throw {
      status: res.status,
      detail: detailMessage,
    };
  }

  return data;
}

// CAPTCHA Al
export async function getCaptcha() {
  return apiFetch("/contact/captcha");
}

// Mesaj Gönder
export async function sendContactMessage(formData) {
  return apiFetch("/contact/send", {
    method: "POST",
    body: formData,
  });
}