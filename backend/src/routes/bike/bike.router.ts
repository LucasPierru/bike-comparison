import express from "express";
import { httpGetBikes } from "./bike.controller";

const bikeRouter = express.Router();

bikeRouter.get("/", httpGetBikes);

export default bikeRouter;
