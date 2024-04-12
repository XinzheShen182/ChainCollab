import React, { useEffect } from "react";
import { Card, Row, Col, Typography } from "antd";
import { useState } from "react";
import { DeploymentUnitOutlined } from "@ant-design/icons";
import DoneIcon from "@mui/icons-material/Done";
import Chip from "@mui/material/Chip";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ClearIcon from "@mui/icons-material/Clear";
import Icon from "@mdi/react";
import { mdiGamepadCircleOutline } from "@mdi/js";
const { Text } = Typography;

let startIcon = <DoneIcon />;
let pauseIcon = <ClearIcon />;
interface chipProps {
  icon: JSX.Element;
  label: string;
  sx: React.CSSProperties;
}

const customColStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  marginLeft: "0px",
};
const customTextStyle: React.CSSProperties = {
  fontSize: "14px", // 可以调整字体大小以适应新的行高
  display: "flex",
  alignItems: "center",
};

const EndColStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  marginRight: "0px",
};

import { usePeerData } from "./hooks";
import { useAppSelector } from "@/redux/hooks";
const Peer: React.FC = () => {
  const currentEnvId = useAppSelector(state => state.env.currentEnvId)
  const [
    peerList,
    peerListLoaing,
    syncPeerList,
  ] = usePeerData(currentEnvId);

  console.log(peerList, peerListLoaing, syncPeerList)

  return (
    <>
      <Col span={12}>
        <Card title="Peer Nodes" style={{ width: "100%", height: "100%" }} loading={peerListLoaing} >
          {peerList?.map((peerNode) => (
            <Card.Grid
              style={{ width: "100%", height: "100%", cursor: "pointer" }}
              onClick={() => console.log("clicked")}
            >
              <Row style={{ width: "100%", height: "100%" }}>
                <Col span={2} style={customColStyle}>
                  <Icon path={mdiGamepadCircleOutline} size={1} />
                </Col>
                <Col span={6} style={customColStyle}>
                  <Row>
                    <Text strong style={customTextStyle}>
                      {peerNode.name}
                    </Text>
                  </Row>
                </Col>
                <Col span={8} style={customColStyle}>
                  <Row>
                    <Text style={customTextStyle}>{peerNode.Membership}</Text>
                  </Row>
                </Col>
                {/* <Col span={7} style={customColStyle}>
                  <Chip {...peerNode.chipProps} />
                </Col> */}
                <Col flex="auto" style={{...EndColStyle, width:"200px"}} >
                  <Text style={customTextStyle}>{peerNode.owner}</Text>
                </Col>
                <Col
                  flex="auto"
                  style={{
                    ...EndColStyle,
                    textAlign: "right",
                    marginRight: "0px",
                  }}
                >
                  <KeyboardArrowRightIcon />
                </Col>
              </Row>
            </Card.Grid>
          ))}
        </Card>
      </Col>
    </>
  );
};

export default Peer;
