﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using UnityEngine.UI; //Need this for calling UI scripts

using SLS.Widgets.Table; //Need this for calling table pro

public class CutAndFillManager : MonoBehaviour {

    // max points for the table
    const int MAXPOINTS = 20;

    // setup arrays for cut/fill data and mass haul data
    float[] station       = new float[MAXPOINTS];
    float[] existGrade    = new float[MAXPOINTS];
    float[] propGrade     = new float[MAXPOINTS];
    float[] roadWidth     = new float[MAXPOINTS];
    float[] cutArea       = new float[MAXPOINTS];
    float[] fillArea      = new float[MAXPOINTS];
    float[] cutVolume     = new float[MAXPOINTS];
    float[] fillVolume    = new float[MAXPOINTS];
    float[] adjFillVolume = new float[MAXPOINTS];
    float[] algebraicSum  = new float[MAXPOINTS];
    float[] massOrdinate  = new float[MAXPOINTS];

    [SerializeField]
    Transform UIPanel; //Will assign our panel to this variable so we can enable/disable it

    // variables for getting the terrain object and terrain height
    public GameObject terrain;
    private TerrainGenerator terrainHeight;

    // variables for getting the road object and road points
    public GameObject road;
    private Road roadPoint;

    // timer variables, used for testing table update function
    float timer = 0f;
    float waitingTime = 5f;

    // handle to actual data table
    private Table table;

    void Start()
    {   
        // get terrain object
        terrain = GameObject.Find("Terrain");
        // get height function from terrain generator
        terrainHeight = terrain.GetComponent<TerrainGenerator>();

        // get road object
        road = GameObject.Find("Road");
        // get point from road
        roadPoint = road.GetComponent<Road>();

        // get the table attached to the cut/fill panel
        table = GetComponent<Table>();

        updateTable();

        UIPanel.gameObject.SetActive(false); //make sure our pause menu is disabled when scene starts
    }

    // Update is called once per frame
    void Update()
    {
        // timer for testing table updates
        timer += Time.deltaTime;
        if (timer > waitingTime)
        {
            timer = 0f;

            updateTable();
        }
    }

    // Handle the row selection however you wish
    private void onTableSelected(Datum datum)
    {
        print("You Clicked: " + datum.uid);
    }

    public void Pause()
    {
        UIPanel.gameObject.SetActive(true); //turn on the pause menu
    }

    public void UnPause()
    {
        UIPanel.gameObject.SetActive(false); //turn off pause menu
    }

    void updateTable()
    {
        // reset the table before updating it
        table.ResetTable();

        // add the column headers
        table.AddTextColumn("Station (ft)");
        table.AddTextColumn("Existing Gr (ft)");
        table.AddTextColumn("Proposed Gr (ft)");
        table.AddTextColumn("Roadway Width (ft)");
        table.AddTextColumn("Cut Area (ft)");
        table.AddTextColumn("Fill Area (sf)");
        table.AddTextColumn("Cut Volumes (bcy)");
        table.AddTextColumn("Fill Volumes (ccy)");
        table.AddTextColumn("Adj. Fill Volumes (bcy)");
        table.AddTextColumn("Algebraic Sum (cy)");
        table.AddTextColumn("Mass Ordinate (cy)");

        // Initialize Your Table
        table.Initialize(onTableSelected);

        // update values
        updateStation();
        updateExistGrade();
        updatePropGrade();
        updateRoadWidth();
        updateCutArea();
        updateFillArea();
        updateCutVolume();
        updateFillVolume();
        updateAdjFillVolume();
        updateAlgebraicSum();
        updateMassOrdinate();

        // Populate Your Rows
        for (int i = 0; i < MAXPOINTS; i++)
        {
            Datum d = Datum.Body(i.ToString());
            d.elements.Add(station[i].ToString());
            d.elements.Add(existGrade[i].ToString());
            d.elements.Add(propGrade[i].ToString());
            d.elements.Add(roadWidth[i].ToString());
            d.elements.Add(cutArea[i].ToString());
            d.elements.Add(fillArea[i].ToString());
            d.elements.Add(cutVolume[i].ToString());
            d.elements.Add(fillVolume[i].ToString());
            d.elements.Add(adjFillVolume[i].ToString());
            d.elements.Add(algebraicSum[i].ToString());
            d.elements.Add(massOrdinate[i].ToString());
            table.data.Add(d);
        }

        // Draw Your Table
        table.StartRenderEngine();
    }

    void updateStation()
    {
        // first station is always zero
        station[0] = 0;

        // get the road points from the road object
        Vector3[] positions = roadPoint.GetRoadPoints();

        for (int i = 1; i < MAXPOINTS; i++)
        {
            // calcuate the station distances using vector distance function
            station[i] = station[i - 1] +  Vector3.Distance(positions[i - 1], positions[i]);
            //Debug.Log("STATION #" + i + " value " + station[i]);
        }
    }

    void updateExistGrade()
    {
        Vector3[] positions = roadPoint.GetRoadPoints();

        for (int i = 0; i < MAXPOINTS; i++)
        {
            // existing grade is basically the road distance from the terrain
            existGrade[i] = terrainHeight.GetHeightAtWorldPosition(positions[i]);
            //Debug.Log("EXISTING GRADE #" + i + " value " + existGrade[i]);
        } 
    }

    void updatePropGrade()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // proposed grade or road height after cut/fill, can be changed in the future
            propGrade[i] = 0;
            //Debug.Log("PROPOSED GRADE #" + i + " value " + propGrade[i]);
        }
    }

    void updateRoadWidth()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // width of the road, can be changed in the future
            roadWidth[i] = 120;
            //Debug.Log("ROAD WIDTH #" + i + " value " + roadWidth[i]);
        }
    }

    void updateCutArea()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // if terrain above road, then cut
            if (existGrade[i] > 0)
            {
                cutArea[i] = (existGrade[i] * existGrade[i]) + (roadWidth[i] * existGrade[i]);
            }
            else
            {
                cutArea[i] = 0;
            }
            //Debug.Log("CUT AREA #" + i + " value " + cutArea[i]);
        }
    }

    void updateFillArea()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // if terrain below road, then fill
            if (existGrade[i] <= 0)
            {
                fillArea[i] = -1 * ((existGrade[i] * existGrade[i]) + Mathf.Abs(roadWidth[i] * existGrade[i]));
            }
            else
            {
                fillArea[i] = 0;
            }
            //Debug.Log("FILL AREA #" + i + " value " + fillArea[i]);
        }
    }

    void updateCutVolume()
    {
        cutVolume[0] = 0;

        for (int i = 1; i < MAXPOINTS; i++)
        {
            // use cut area to calculate cut volume
            cutVolume[i] = (cutArea[i] + cutArea[i - 1]) / 2 * (station[i] - station[i - 1]) / 27;
            //Debug.Log("CUT VOLUME #" + i + " value " + cutVolume[i]);
        }
    }

    void updateFillVolume()
    {
        fillVolume[0] = 0;

        for (int i = 1; i < MAXPOINTS; i++)
        {
            // use fill area to calculate fill volume
            fillVolume[i] = (fillArea[i] + fillArea[i - 1]) / 2 * (station[i] - station[i - 1]) / 27;
            //Debug.Log("FILL VOLUME #" + i + " value " + fillVolume[i]);
        }
    }

    void updateAdjFillVolume()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // adjusted fill volume (convert from compacted cubic yards to bank cubic yards)
            adjFillVolume[i] = fillVolume[i] / 0.9f;
            //Debug.Log("ADJUSTED FILL VOLUME #" + i + " value " + adjFillVolume[i]);
        }
    }

    void updateAlgebraicSum()
    {
        for (int i = 0; i < MAXPOINTS; i++)
        {
            // cut vol - fill vol (algebraicSum is used to calculate mass ordinates)
            algebraicSum[i] = cutVolume[i] + adjFillVolume[i];
            //Debug.Log("ALGEBRAIC SUM #" + i + " value " + algebraicSum[i]);
        }
    }

    void updateMassOrdinate()
    {
        massOrdinate[0] = algebraicSum[0];

        for (int i = 1; i < MAXPOINTS; i++)
        {
            /* (cumulative sum, aka mass ordinate)
             * Used to figure out how much excess and deficit material available after 
             * all cut material used for required fill in each section.
             */
            massOrdinate[i] = massOrdinate[i - 1] + algebraicSum[i];
            //Debug.Log("MASS ORDINATE #" + i + " value " + massOrdinate[i]);
        }
    }
}
