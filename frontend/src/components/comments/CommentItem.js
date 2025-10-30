import React, { useState } from "react";
import CommentForm from "./CommentForm";
import commentService from "../../services/commentService";
import { useAuth } from "../../contexts/AuthContext";
import "../../styles/components/comments.css";

function CommentItem({ comment, depth = 0, onCommentAdded }) {
  const { user } = useAuth();
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [currentContent, setCurrentContent] = useState(comment.content);

  const handleReply = async (content) => {
    await commentService.replyToComment(comment.id, content);
    setShowReplyForm(false);
    if (onCommentAdded) onCommentAdded(); // Recharger tout
  };

  const handleEdit = async () => {
    if (!editContent.trim()) {
      alert("Le commentaire ne peut pas être vide");
      return;
    }

    try {
      await commentService.updateComment(comment.id, editContent);
      setCurrentContent(editContent);
      setIsEditing(false);
      if (onCommentAdded) onCommentAdded(); // Recharger tout
    } catch (error) {
      console.error("Erreur modification:", error);
      alert("Erreur lors de la modification");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Supprimer ce commentaire ?")) return;

    try {
      await commentService.deleteComment(comment.id);
      if (onCommentAdded) onCommentAdded(); // Recharger tout
    } catch (error) {
      console.error("Erreur suppression:", error);
      alert("Erreur lors de la suppression");
    }
  };

  const authorName = comment.author
    ? comment.author.username
    : "[Compte supprimé]";

  const canEdit = user && (
    comment.author?.id === user.id || 
    user.profile?.role === 'admin'
  );

  return (
    <div className={`comment-item ${depth > 0 ? "comment-item--nested" : ""}`}>
      <div className="comment-box">
        <div className="comment-header">
          <span className="comment-author">{authorName}</span>
          <span className="comment-date">
            {" "}
            - {new Date(comment.created_at).toLocaleString()}
          </span>
          {comment.is_edited && (
            <span className="comment-edited"> (modifié)</span>
          )}
        </div>

        {isEditing ? (
          <div className="comment-edit-form">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="comment-edit-textarea"
              rows="3"
            />
            <div className="comment-edit-actions">
              <button onClick={handleEdit} className="btn-save">
                Enregistrer
              </button>
              <button 
                onClick={() => {
                  setIsEditing(false);
                  setEditContent(currentContent);
                }} 
                className="btn-cancel"
              >
                Annuler
              </button>
            </div>
          </div>
        ) : (
          <div className="comment-content">{currentContent}</div>
        )}

        <div className="comment-actions">
          <button onClick={() => setShowReplyForm(!showReplyForm)}>
            {showReplyForm ? "Annuler" : "Répondre"}
          </button>
          
          {canEdit && !isEditing && (
            <>
              <button onClick={() => setIsEditing(true)} className="btn-edit">
                Modifier
              </button>
              <button onClick={handleDelete} className="btn-delete">
                Supprimer
              </button>
            </>
          )}
        </div>
      </div>

      {showReplyForm && (
        <div className="comment-reply-form">
          <CommentForm
            onSubmit={handleReply}
            placeholder="Écrire une réponse..."
          />
        </div>
      )}

      {/* Utiliser directement comment.replies au lieu d'un état local */}
      {comment.replies && comment.replies.map((reply) => (
        <CommentItem
          key={reply.id}
          comment={reply}
          depth={depth + 1}
          onCommentAdded={onCommentAdded}
        />
      ))}
    </div>
  );
}

export default CommentItem;