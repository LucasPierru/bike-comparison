import express from "express";
import cors from "cors";
import api from "./routes/api";
import passport from "passport";
/* import "./passport"; */

const app = express();

app.use(
  cors({
    origin: "http://localhost:3000",
    credentials: true,
  })
);
app.use(express.json());
app.use(passport.initialize());
app.use("/v1", api);

export default app;
