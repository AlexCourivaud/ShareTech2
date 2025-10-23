import React, { useState } from "react";
import "../../styles/components/comments.css";

function CommentForm({ onSubmit, placeholder = "Écrire un commentaire..." }) {
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!content.trim()) return;

    setLoading(true);
    try {
      await onSubmit(content);
      setContent("");
    } catch (error) {
      console.error("Erreur création commentaire:", error);
      alert("Erreur lors de l'envoi du commentaire");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="comment-form">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={placeholder}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !content.trim()}>
        {loading ? "Envoi..." : "Envoyer"}
      </button>
    </form>
  );
}

export default CommentForm;
