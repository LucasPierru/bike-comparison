import express from 'express';
import { httpGetBrands, httpSearchBrand } from './brand.controller';

const brandRouter = express.Router();

brandRouter.get('/', httpGetBrands);
brandRouter.get('/search', httpSearchBrand);

export default brandRouter;
