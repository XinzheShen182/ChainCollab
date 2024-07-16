import { useEffect, useState } from "react"
import { Card, Row, Col, Button, Steps, Modal, Table, Select, Input } from "antd"
import { useLocation, useNavigate } from "react-router-dom";
import { retrieveBPMN, packageBpmn, updateBPMNStatus, updateBpmnEnv, updateBPMNFireflyUrl } from "@/api/externalResource"
import { generateChaincode } from "@/api/translator"
import { useAvaliableEnvs, useBpmnDetailData } from "./hooks"
import axios from "axios"
const steps = [
    {
        title: "Initiated",
    },
    {
        title: 'DeployEnved',
    },
    {
        title: 'Generated',
    },
    {
        title: 'Installed',
    },
    {
        title: 'Registered',
    },
];

import { useAppSelector } from "@/redux/hooks";
import { getAllMessages, registerDataType, initLedger } from "@/api/executionAPI"
import { current_ip } from "@/api/apiConfig";

const BPMNOverview = () => {

    const location = useLocation();
    const bpmnId = location.pathname.split("/").pop();
    // const bpmnInstanceId = location.pathname.split("/").pop();
    const [isBindingModelOpen, setIsBindingModelOpen] = useState(false);
    const [isEnvModalOpen, setIsEnvModalOpen] = useState(false);
    const currentOrgId = useAppSelector((state) => state.org.currentOrgId);
    const [buttonLoading, setButtonLoading] = useState(false);
    const [isModifyModalOpen, setIsModifyModalOpen] = useState(false);
    const [chainCodeContentForModify, setChainCodeContentForModify] = useState("");
    const [ffiContentForModify, setFFIContentForModify] = useState("");


    const navigate = useNavigate();
    const [bpmn, { isLoading, isError, isSuccess }, refetchBpmn] = useBpmnDetailData(bpmnId);

    const status = bpmn.status;
    const currentNumber = ((status: string) => {
        switch (status) {
            case "Initiated":
                return 0;
            case "DeployEnved":
                return 1;
            case "Generated":
                return 2;
            case "Installed":
                return 3;
            case "Registered":
                return 4;
        }
    })(status);


    const EnvModal = ({
        open, setOpen
    }) => {
        const [envId, setEnvId] = useState("");
        const [envs, refetchEnvs] = useAvaliableEnvs(currentConsortiumId);

        return (
            <Modal
                title="Select Env"
                open={open}
                onOk={async () => {
                    await updateBpmnEnv(bpmnId, envId);
                    await updateBPMNStatus(bpmnId, "DeployEnved");
                    refetchBpmn()
                    setButtonLoading(false);
                    setOpen(false)
                }}
                onCancel={() => {
                    setButtonLoading(false);
                    setOpen(false)
                }}
            >
                <Select
                    style={{ width: "100%" }}
                    placeholder="Select a env to deploy"
                    optionFilterProp="children"
                    onChange={
                        (value) => {
                            setEnvId(envs.find((env) => env.id == value).id);
                        }
                    }
                >
                    {envs.map((env) => (
                        <Select.Option value={env.id}>{env.name}</Select.Option>
                    ))}
                </Select>
            </Modal>
        )
    }

    const ModifyModal = () => {

        const onModify = async () => {
            await packageBpmn(chainCodeContentForModify, ffiContentForModify, currentOrgId, bpmnId);
            refetchBpmn()
            setButtonLoading(false);
        }

        return (
            <Modal
                title="Modify"
                open={isModifyModalOpen}
                onCancel={async () => {
                    setButtonLoading(false);
                    setIsModifyModalOpen(false);
                }}
                onOk={async () => {
                    onModify();
                    setIsModifyModalOpen(false);
                }}
                width={'40%'}
            >
                <h1>ChainCode</h1>
                <Input.TextArea
                    value={chainCodeContentForModify}
                    onChange={(e) => {
                        setChainCodeContentForModify(e.target.value);
                    }}
                    style={{
                        width: "1000px",
                        height: "300px",
                    }}
                />
                <h2>FFI</h2>
                <Input.TextArea
                    value={ffiContentForModify}
                    onChange={(e) => {
                        setFFIContentForModify(e.target.value);
                    }}
                    style={{
                        width: "1000px",
                        height: "300px",
                    }}
                />
            </Modal>
        )
    }

    const onGenerate = async () => {
        try {
            setButtonLoading(true);
            const bpmn = await retrieveBPMN(bpmnId);
            const res = await generateChaincode(bpmn.bpmnContent);
            const chaincode_content = res.bpmnContent;
            const ffi_content = res.ffiContent;
            setChainCodeContentForModify(chaincode_content);
            setFFIContentForModify(ffi_content);
            setIsModifyModalOpen(true);
            // await packageBPMN(chaincode_content, ffi_content, bpmnInstanceId, currentOrgId);
            // syncInstance()
            // setButtonLoading(false);
        } catch (e) {
            console.log(e);
        }
    }

    const onDeployEnv = async () => {
        try {
            setButtonLoading(true);
            setIsEnvModalOpen(true);
        } catch (e) {
            console.log(e);
        }
    }

    const onRegister = async () => {
        try {
            setButtonLoading(true);
            const bpmn = await retrieveBPMN(bpmnId)
            const chaincodeName = bpmn.name.replace(".bpmn", "")
            const ffiContent = bpmn.ffiContent
            const parsedFFIContent = JSON.parse(ffiContent);
            const chaincodeIdPrefix = chaincodeName + "-" + bpmn.chaincode.substring(0, 6);
            parsedFFIContent.name = chaincodeIdPrefix;
            const response = await axios.post(`${current_ip}:5000/api/v1/namespaces/default/contracts/interfaces`,
                parsedFFIContent)
            const interfaceid = response.data.id;
            const location = {
                channel: "default",        //写死在后端
                chaincode: chaincodeName
            };
            const jsonData = {
                name: response.data.name,  //接口id名字改为bpmninstanceid
                interface: {
                    id: interfaceid
                },
                location: location
            };
            await new Promise(resolve => setTimeout(resolve, 4000));
            const response2 = await axios.post(`${current_ip}:5000/api/v1/namespaces/default/apis`,
                jsonData)
            const fireflyUrl = response2.data.urls.ui
            await new Promise(resolve => setTimeout(resolve, 4000));
            const fireflyUrlForRegister = `${current_ip}:5000`
            await initLedger(fireflyUrlForRegister, chaincodeIdPrefix);
            await new Promise(resolve => setTimeout(resolve, 4000));
            // 目前无法通过getAllMessage获取所有的message,因为需要实例ID查询消息。此处应该通过BPMN内容提取出所有消息的properties字段
            // const messages = await getAllMessages(fireflyUrlForRegister, chaincodeIdPrefix);

            // const all_requests = messages ? messages.map(
            //     (msg) => {
            //         console.log()
            //         const data1 = {
            //             "$id": "https://example.com/widget.schema.json",
            //             "$schema": "https://json-schema.org/draft/2020-12/schema",
            //             "title": "Widget",
            //             "type": "object"
            //         }
            //         let data2 = {}
            //         try {
            //             data2 = JSON.parse(msg.format)
            //             data2 = {
            //                 "properties": data2["properties"],
            //                 "required": data2["required"],
            //             }
            //         } catch (e) {
            //             console.log(e)
            //             return;
            //         }

            //         const mergeData = {
            //             "name": chaincodeName + "_" + msg.messageID,
            //             "version": "1",
            //             "value": {
            //                 ...data1,
            //                 ...data2
            //             }
            //         }
            //         return registerDataType(
            //             fireflyUrlForRegister,
            //             mergeData
            //         )
            //     }
            // ) : [];
            // const res2 = await Promise.all(all_requests)
            await updateBPMNFireflyUrl(bpmnId, fireflyUrl);
            const res = await updateBPMNStatus(bpmnId, "Registered");
            refetchBpmn()
            setButtonLoading(false);
        } catch (error) {
            console.error("Error occurred while making post request:", error);
        }
    }

    const currentEnvId = useAppSelector((state) => state.env.currentEnvId);
    const currentConsortiumId = useAppSelector((state) => state.consortium.currentConsortiumId);

    const buttonText = (() => {
        if (status == 'Installed') {
            return 'Register';
        } else if (status == 'Registered') {
            return 'Execute';
        }
        else if (status == 'Initiated') {
            return 'Deploy to Env';
        }
        else {
            return status == 'Generated' ? 'Install' : 'Generate';
        }
    })()

    return (
        <>
            <Card title="Overview" style={{ width: "100%" }}>
                <Card.Grid style={{ width: "100%", height: "100%" }}>
                    <Row
                        justify="end"
                        style={{ width: "100%", height: "100%" }}
                    >
                        <Col
                            flex="auto"
                            style={{ textAlign: "right", marginRight: "0px" }}
                        >
                            {/* <Button type="primary"
                            style={{ marginRight: "10px", display: status == "Initiated" ? "" : "none" }}
                            onClick={() => {
                                setIsBindingModelOpen(true);
                            }} >BINDING</Button> */}
                            <Button type="primary"
                                // disabled={status == 'Initiated'}
                                loading={buttonLoading}
                                onClick={() => {
                                    if (status == 'Generated') {
                                        navigate(`/orgs/${currentOrgId}/consortia/${currentConsortiumId}/envs/${currentEnvId}/fabric/chaincode`)
                                    } else if (status == 'Installed') {
                                        onRegister();
                                    } else if (status == 'Initiated') {
                                        onDeployEnv();
                                    } else if (status == 'DeployEnved') {
                                        onGenerate();
                                    }
                                }} >{buttonText}</Button>
                        </Col>
                    </Row>
                    <Row>
                        <Col
                            style={{
                                marginLeft: "40px",
                                width: "100%",
                                marginTop: "10px",
                            }}
                        >
                            <Steps
                                current={currentNumber}
                                items={steps}
                            />
                        </Col>
                    </Row>
                </Card.Grid>
            </Card>
            {
                ModifyModal()
            }
            {
                <EnvModal open={isEnvModalOpen} setOpen={setIsEnvModalOpen} />
            }
        </>


    )

}


export default BPMNOverview;