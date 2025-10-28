import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Button from "../common/Button";
import "../../styles/components/navbar.css";

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar__container">
        <Link to="/dashboard" className="navbar__logo">
          ShareTech
        </Link>

        <div className="navbar__actions">
          <span className="navbar__user">👤 {user?.username}</span>
          <Button onClick={handleLogout} variant="secondary">
            Déconnexion
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
