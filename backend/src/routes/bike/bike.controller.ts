import { Request, Response } from 'express';
import Bike from 'models/bike.mongo';

export const httpGetBikes = async (req: Request, res: Response) => {
  try {
    const bikes = await Bike.find();
    res.status(200).json({ bikes });
  } catch (error) {
    res
      .status(500)
      .json({ message: `Cannot access bikes ${req.params.id}`, error });
  }
};
