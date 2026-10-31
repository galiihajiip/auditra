import "vis-network/styles/vis-network.min.css";
import { ThemeProvider } from "./theme/ThemeContext";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}
