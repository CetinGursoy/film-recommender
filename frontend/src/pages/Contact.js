import React, { useState, useRef } from "react";
import "./Contact.css";
import { sendContactMessage } from "../api";
import ReCAPTCHA from "react-google-recaptcha";

export default function Contact() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [captchaToken, setCaptchaToken] = useState(null);
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loading, setLoading] = useState(false);

  const recaptchaRef = useRef(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCaptchaChange = (token) => {
    setCaptchaToken(token);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: "", message: "" });

    try {
      if (!captchaToken) {
        throw new Error("Lütfen 'Robot değilim' kutucuğunu işaretleyin.");
      }

      await sendContactMessage({
        name: formData.name,
        email: formData.email,
        message: formData.message,
        captcha_token: captchaToken,
      });

      setStatus({ type: "success", message: "Mesajınız başarıyla iletildi! 🚀" });
      setFormData({ name: "", email: "", message: "" });
      setCaptchaToken(null);
      if (recaptchaRef.current) {
        recaptchaRef.current.reset();
      }
    } catch (err) {
      setStatus({ type: "error", message: err.detail || err.message || "Bir hata oluştu." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contact-container">
      <div className="contact-box">
        <h1 className="contact-title">İletişim</h1>
        <p className="contact-subtitle">Görüş, öneri ve mesajlarını bize ilet.</p>

        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        )}

        <form className="contact-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Adınız"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="email"
            placeholder="E-posta adresiniz"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <textarea
            name="message"
            placeholder="Mesajınız"
            value={formData.message}
            onChange={handleChange}
            required
          ></textarea>

          <div className="captcha-container" style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
            <ReCAPTCHA
              ref={recaptchaRef}
              sitekey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI" // TEST KEY - REPLACE IN PRODUCTION
              onChange={handleCaptchaChange}
            />
          </div>

          <button type="submit" className="contact-btn" disabled={loading}>
            {loading ? "Gönderiliyor..." : "Gönder 🚀"}
          </button>
        </form>
      </div>
    </div>
  );
}
