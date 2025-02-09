import { Request, Response } from 'express';
import Component from '../../models/component.mongo';

export const httpGetComponents = async (req: Request, res: Response) => {
  try {
    const components = await Component.find();
    res.status(200).json({ components });
  } catch (error) {
    res.status(500).json({ message: `Cannot access components`, error });
  }
};
