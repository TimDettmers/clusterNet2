#include <boost/thread.hpp>
#include <boost/date_time.hpp>
#include <iostream>
#include <basicOps.cuh>
#include <cublas_v2.h>
#include <curand.h>
#include <cuda.h>
#include "nervana_c_api.h"
#include "leveldb/db.h"

#ifndef __ClusterNet_H__
#define __ClusterNet_H__

typedef enum Unittype_t
{
	Logistic = 0,
	Rectified_Linear = 1,
	Softmax = 2,
	Linear = 4,
	Input = 8
} Unittype_t;

typedef enum DataPropagationType_t
{
	Training = 0,
	Trainerror = 1,
	CVerror = 2
} DataPropagationType_t;


typedef enum WeightUpdateType_t
{
	RMSProp = 0,
	Momentum = 1,
	PlainSGD = 2
} WeightUpdateType_t;

typedef enum Costfunction_t
{
	Cross_Entropy = 0,
	Squared_Error = 1,
	Root_Squared_Error = 2,
	Misclassification = 4
} Costfunction_t;


class ClusterNet
{
    public:
        ClusterNet();
  		void setRandomState(int seed);
  		Matrix<float> *rand(int rows, int cols);
  		Matrix<float> *randn(int rows, int cols);
  		Matrix<float> *normal(int rows, int cols, float mean, float std);

  		void Tdot(Matrix<float> *A, Matrix<float> *B, Matrix<float> *out);
  		void dotT(Matrix<float> *A, Matrix<float> *B, Matrix<float> *out);
  		void dot(Matrix<float> *A, Matrix<float> *B, Matrix<float> *out);
  		void dot(Matrix<float> *A, Matrix<float> *B, Matrix<float> *out, bool T1, bool T2);
  	    void dropout(Matrix<float> *A, Matrix <float> *out, const float dropout);
    private:
  		curandGenerator_t m_generator;

};



#endif //__ClusterNet_H__