import express from "express";
import bikeRouter from "./bike/bike.router";
import brandRouter from "./brand/brand.router";

const api = express.Router();

api.use("/bike", bikeRouter);
api.use("/brand", brandRouter);

export default api;
