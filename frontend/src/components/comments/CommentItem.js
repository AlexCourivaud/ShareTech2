import React, { useState } from "react";
import CommentForm from "./CommentForm";
import commentService from "../../services/commentService";
import "../../styles/components/comments.css";

function CommentItem({ comment, depth = 0, onCommentAdded }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replies, setReplies] = useState(comment.replies || []);

  const handleReply = async (content) => {
    const newReply = await commentService.replyToComment(comment.id, content);
    setReplies([...replies, newReply]);
    setShowReplyForm(false);
    if (onCommentAdded) onCommentAdded();
  };

  const authorName = comment.author
    ? comment.author.username
    : "[Compte supprimé]";

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

        <div className="comment-content">{comment.content}</div>

        <div className="comment-actions">
          <button onClick={() => setShowReplyForm(!showReplyForm)}>
            {showReplyForm ? "Annuler" : "Répondre"}
          </button>
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

      {replies.map((reply) => (
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
