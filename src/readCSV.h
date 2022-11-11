#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

//----------------------------------------------------------------------------
// Notice how the data is stored as a 2D deque. This accomodates huge files.
// I could use a vector instead if I also know the input files are small.
//
struct data_t : deque<deque<double>>
{
    typedef deque<deque<double>>::iterator record_iterator;
    typedef deque<double>::iterator field_iterator;
    bool load(const string &filename);
    bool save(const string &filename);
    bool save(ostream &outs);
};

//----------------------------------------------------------------------------
bool data_t::load(const string &filename)
{
    string s;
    ifstream f(filename.c_str());
    while (getline(f, s))
    {
        deque<double> record;
        istringstream iss(s);
        while (getline(iss, s, ','))
        {
            double fieldvalue = 0.0f;
            istringstream(s) >> fieldvalue;
            record.push_back(fieldvalue);
        }
        this->push_back(record);
    }
    return f.good();
}

//----------------------------------------------------------------------------
bool data_t::save(const string &filename)
{
    ofstream f(filename.c_str());
    if (!f)
        return false;

    return save(f);
}

//----------------------------------------------------------------------------
bool data_t::save(ostream &outs)
{
    for (data_t::record_iterator ri = this->begin(); ri != this->end(); ri++)
    {
        for (data_t::field_iterator fi = ri->begin(); fi != ri->end(); fi++)
            outs << ((fi == ri->begin()) ? "" : ", ") << *fi;
        outs << endl;
    }
    return outs.good();
}

//----------------------------------------------------------------------------
