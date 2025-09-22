import React from "react";
import { createRoot } from "react-dom/client";
import "./styles/index.css";  // Chemin vers styles/
import App from "./App";

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);  // Cette ligne manque