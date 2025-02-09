import { Request, Response } from 'express';
import Bike from '../../models/bike.mongo';

export const httpGetBikes = async (req: Request, res: Response) => {
  const { perPage, page } = req.query;

  const perPageNum = Number(perPage) || 10;
  const pageNum = Number(page) || 0;

  try {
    const bikes = await Bike.find({
      $text: { $search: 'road' }
    })
      .limit(perPageNum)
      .skip(pageNum * perPageNum);
    res.status(200).json({ bikes });
  } catch (error) {
    res
      .status(500)
      .json({ message: `Cannot access bikes ${req.params.id}`, error });
  }
};
