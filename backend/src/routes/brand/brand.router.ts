import express from "express";
import { httpGetBrands } from "./brand.controller";

const brandRouter = express.Router();

brandRouter.get("/", httpGetBrands);

export default brandRouter;
