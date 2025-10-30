import React, { useState, useEffect } from "react";
import commentService from "../../services/commentService";
import CommentForm from "./CommentForm";
import CommentItem from "./CommentItem";
import "../../styles/components/comments.css";

function CommentSection({ noteId }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadComments = async () => {
    try {
      const data = await commentService.getCommentsByNote(noteId);
      setComments(data);
    } catch (error) {
      console.error("Erreur chargement commentaires:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComments();
  }, [noteId]);

  const handleNewComment = async (content) => {
    const newComment = await commentService.createComment(noteId, content);
    // Recharger tous les commentaires pour avoir la structure complète
    loadComments();
  };

  if (loading) {
    return (
      <div className="comment-section">Chargement des commentaires...</div>
    );
  }

  return (
    <div className="comment-section">
      <h3>Commentaires ({comments.length})</h3>

      <CommentForm onSubmit={handleNewComment} />

      {comments.length === 0 ? (
        <p className="empty-comments">Aucun commentaire pour le moment.</p>
      ) : (
        comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onCommentAdded={loadComments}
          />
        ))
      )}
    </div>
  );
}

export default CommentSection;