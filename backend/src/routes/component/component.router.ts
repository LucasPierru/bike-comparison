import express from 'express';
import { httpGetComponents } from './component.controller';

const componentRouter = express.Router();

componentRouter.get('/', httpGetComponents);

export default componentRouter;
