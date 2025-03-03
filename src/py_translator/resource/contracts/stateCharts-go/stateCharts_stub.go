package main

import (
	"IBC/StateCharts/stateCharts"
	"fmt"
	"log"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

func main() {
	fmt.Println("Starting StateCharts chaincode")
	bpmnChaincode, err := contractapi.NewChaincode(&stateCharts.StateCharts{})
	if err != nil {
		log.Panicf("Error creating bpmn chaincode: %v", err)
	}

	if err := bpmnChaincode.Start(); err != nil {
		log.Panicf("Error starting bpmn chaincode: %v", err)
	}
}
